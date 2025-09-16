"""
Sistema de tracking de costos para agentes IA
Monitorea uso y costos en tiempo real con Redis
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from decimal import Decimal
import redis.asyncio as redis
import redis as sync_redis
import tiktoken
from pydantic import BaseModel

from services.ai.config import ai_config, ModelType, AIProvider

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Métricas de uso de un agente"""
    timestamp: datetime
    agent_type: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    response_time: float
    chat_id: Optional[int] = None
    user_id: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None

class CostSummary(BaseModel):
    """Resumen de costos por período"""
    period: str
    total_cost: float
    total_requests: int
    total_tokens: int
    breakdown_by_agent: Dict[str, float]
    breakdown_by_model: Dict[str, float]
    most_expensive_request: float
    average_cost_per_request: float
    success_rate: float

class CostTracker:
    """Tracker principal de costos y métricas"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.daily_limit = ai_config.daily_cost_limit
        self.monthly_limit = ai_config.monthly_cost_limit
        self.encoding_cache = {}
        
    async def init_redis(self):
        """Inicializa conexión Redis"""
        try:
            self.redis_client = redis.from_url(ai_config.redis_url)
            await self.redis_client.ping()
            logger.info("Redis conectado para tracking de costos")
        except Exception as e:
            logger.error(f"Error conectando Redis: {str(e)}")
            self.redis_client = None
    
    def get_token_encoder(self, model: ModelType) -> tiktoken.Encoding:
        """Obtiene encoder de tokens para un modelo específico"""
        if model not in self.encoding_cache:
            try:
                if "gpt" in model.value:
                    self.encoding_cache[model] = tiktoken.encoding_for_model(model.value)
                else:
                    # Para Gemini y otros, usar aproximación con cl100k_base
                    self.encoding_cache[model] = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Error obteniendo encoder para {model}: {str(e)}")
                self.encoding_cache[model] = tiktoken.get_encoding("cl100k_base")
        
        return self.encoding_cache[model]
    
    def count_tokens(self, text: str, model: ModelType) -> int:
        """Cuenta tokens en un texto para un modelo específico"""
        try:
            encoder = self.get_token_encoder(model)
            return len(encoder.encode(text))
        except Exception as e:
            logger.error(f"Error contando tokens: {str(e)}")
            # Estimación conservadora: ~4 caracteres por token
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: ModelType) -> Dict[str, float]:
        """Calcula costo basado en tokens y modelo"""
        cost_config = ai_config.get_cost_config(model)
        if not cost_config:
            return {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}
        
        input_cost = (input_tokens / 1000) * cost_config.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * cost_config.output_cost_per_1k_tokens
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    async def track_usage(self, 
                         agent_type: str,
                         model: ModelType,
                         provider: AIProvider,
                         input_text: str,
                         output_text: str,
                         response_time: float,
                         chat_id: Optional[int] = None,
                         user_id: Optional[int] = None,
                         success: bool = True,
                         error_message: Optional[str] = None) -> UsageMetrics:
        """
        Registra uso y calcula costos
        """
        try:
            # Contar tokens
            input_tokens = self.count_tokens(input_text, model)
            output_tokens = self.count_tokens(output_text, model)
            
            # Calcular costos
            costs = self.calculate_cost(input_tokens, output_tokens, model)
            
            # Crear métricas
            metrics = UsageMetrics(
                timestamp=datetime.now(),
                agent_type=agent_type,
                model=model.value,
                provider=provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost=costs["input_cost"],
                output_cost=costs["output_cost"],
                total_cost=costs["total_cost"],
                response_time=response_time,
                chat_id=chat_id,
                user_id=user_id,
                success=success,
                error_message=error_message
            )
            
            # Guardar en Redis si está disponible
            if self.redis_client and ai_config.cost_tracking_enabled:
                await self._save_metrics_redis(metrics)
            
            # Log para debugging
            logger.info(f"Uso registrado - Agente: {agent_type}, Modelo: {model.value}, "
                       f"Tokens: {input_tokens}+{output_tokens}, Costo: ${costs['total_cost']:.6f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}")
            # Retornar métricas básicas en caso de error
            return UsageMetrics(
                timestamp=datetime.now(),
                agent_type=agent_type,
                model=model.value,
                provider=provider.value,
                input_tokens=0,
                output_tokens=0,
                input_cost=0.0,
                output_cost=0.0,
                total_cost=0.0,
                response_time=response_time,
                success=False,
                error_message=f"Error tracking: {str(e)}"
            )
    
    async def _save_metrics_redis(self, metrics: UsageMetrics):
        """Guarda métricas en Redis"""
        try:
            if not self.redis_client:
                return
            
            # Claves para diferentes agregaciones
            today = date.today().isoformat()
            month = today[:7]  # YYYY-MM
            
            # Serializar métricas
            metrics_dict = asdict(metrics)
            metrics_dict['timestamp'] = metrics.timestamp.isoformat()
            
            # Guardar registro individual
            await self.redis_client.lpush(
                f"ai_metrics:{today}",
                json.dumps(metrics_dict)
            )
            
            # Agregar a totales diarios
            await self.redis_client.hincrbyfloat(
                f"ai_costs:daily:{today}",
                "total_cost",
                metrics.total_cost
            )
            await self.redis_client.hincrby(
                f"ai_costs:daily:{today}",
                "total_requests",
                1
            )
            await self.redis_client.hincrby(
                f"ai_costs:daily:{today}",
                "total_tokens",
                metrics.input_tokens + metrics.output_tokens
            )
            
            # Agregar a totales mensuales
            await self.redis_client.hincrbyfloat(
                f"ai_costs:monthly:{month}",
                "total_cost",
                metrics.total_cost
            )
            
            # Totales por agente
            await self.redis_client.hincrbyfloat(
                f"ai_costs:agent:{today}",
                metrics.agent_type,
                metrics.total_cost
            )
            
            # Totales por modelo
            await self.redis_client.hincrbyfloat(
                f"ai_costs:model:{today}",
                metrics.model,
                metrics.total_cost
            )
            
            # Expirar datos antiguos (30 días)
            expire_seconds = 30 * 24 * 60 * 60
            await self.redis_client.expire(f"ai_metrics:{today}", expire_seconds)
            await self.redis_client.expire(f"ai_costs:daily:{today}", expire_seconds)
            await self.redis_client.expire(f"ai_costs:agent:{today}", expire_seconds)
            await self.redis_client.expire(f"ai_costs:model:{today}", expire_seconds)
            
        except Exception as e:
            logger.error(f"Error guardando métricas en Redis: {str(e)}")
    
    async def get_daily_cost(self, date_str: Optional[str] = None) -> float:
        """Obtiene costo total del día"""
        if not self.redis_client:
            return 0.0
        
        if not date_str:
            date_str = date.today().isoformat()
        
        try:
            cost = await self.redis_client.hget(f"ai_costs:daily:{date_str}", "total_cost")
            return float(cost) if cost else 0.0
        except Exception as e:
            logger.error(f"Error obteniendo costo diario: {str(e)}")
            return 0.0
    
    async def get_monthly_cost(self, month_str: Optional[str] = None) -> float:
        """Obtiene costo total del mes"""
        if not self.redis_client:
            return 0.0
        
        if not month_str:
            month_str = date.today().strftime("%Y-%m")
        
        try:
            cost = await self.redis_client.hget(f"ai_costs:monthly:{month_str}", "total_cost")
            return float(cost) if cost else 0.0
        except Exception as e:
            logger.error(f"Error obteniendo costo mensual: {str(e)}")
            return 0.0
    
    async def check_cost_limits(self) -> Dict[str, Any]:
        """Verifica si se han excedido los límites de costo"""
        daily_cost = await self.get_daily_cost()
        monthly_cost = await self.get_monthly_cost()
        
        return {
            "daily": {
                "current": daily_cost,
                "limit": self.daily_limit,
                "exceeded": daily_cost > self.daily_limit,
                "percentage": (daily_cost / self.daily_limit) * 100 if self.daily_limit > 0 else 0
            },
            "monthly": {
                "current": monthly_cost,
                "limit": self.monthly_limit,
                "exceeded": monthly_cost > self.monthly_limit,
                "percentage": (monthly_cost / self.monthly_limit) * 100 if self.monthly_limit > 0 else 0
            }
        }
    
    async def get_cost_summary(self, period: str = "daily") -> CostSummary:
        """Obtiene resumen de costos para un período"""
        try:
            if period == "daily":
                date_str = date.today().isoformat()
                cost_key = f"ai_costs:daily:{date_str}"
                agent_key = f"ai_costs:agent:{date_str}"
                model_key = f"ai_costs:model:{date_str}"
                metrics_key = f"ai_metrics:{date_str}"
            else:
                month_str = date.today().strftime("%Y-%m")
                cost_key = f"ai_costs:monthly:{month_str}"
                # Para mensuales, agregar datos de todos los días del mes
                agent_key = model_key = metrics_key = None
            
            if not self.redis_client:
                return CostSummary(
                    period=period,
                    total_cost=0.0,
                    total_requests=0,
                    total_tokens=0,
                    breakdown_by_agent={},
                    breakdown_by_model={},
                    most_expensive_request=0.0,
                    average_cost_per_request=0.0,
                    success_rate=100.0
                )
            
            # Obtener datos básicos
            cost_data = await self.redis_client.hgetall(cost_key)
            total_cost = float(cost_data.get(b"total_cost", 0))
            total_requests = int(cost_data.get(b"total_requests", 0))
            total_tokens = int(cost_data.get(b"total_tokens", 0))
            
            # Breakdown por agente
            breakdown_by_agent = {}
            if agent_key:
                agent_data = await self.redis_client.hgetall(agent_key)
                breakdown_by_agent = {
                    k.decode(): float(v) for k, v in agent_data.items()
                }
            
            # Breakdown por modelo
            breakdown_by_model = {}
            if model_key:
                model_data = await self.redis_client.hgetall(model_key)
                breakdown_by_model = {
                    k.decode(): float(v) for k, v in model_data.items()
                }
            
            # Análisis de métricas individuales
            most_expensive = 0.0
            success_count = 0
            if metrics_key:
                metrics_list = await self.redis_client.lrange(metrics_key, 0, -1)
                for metric_json in metrics_list:
                    try:
                        metric = json.loads(metric_json)
                        most_expensive = max(most_expensive, metric.get("total_cost", 0))
                        if metric.get("success", True):
                            success_count += 1
                    except:
                        continue
            
            success_rate = (success_count / total_requests * 100) if total_requests > 0 else 100.0
            avg_cost = total_cost / total_requests if total_requests > 0 else 0.0
            
            return CostSummary(
                period=period,
                total_cost=round(total_cost, 6),
                total_requests=total_requests,
                total_tokens=total_tokens,
                breakdown_by_agent=breakdown_by_agent,
                breakdown_by_model=breakdown_by_model,
                most_expensive_request=round(most_expensive, 6),
                average_cost_per_request=round(avg_cost, 6),
                success_rate=round(success_rate, 2)
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de costos: {str(e)}")
            return CostSummary(
                period=period,
                total_cost=0.0,
                total_requests=0,
                total_tokens=0,
                breakdown_by_agent={},
                breakdown_by_model={},
                most_expensive_request=0.0,
                average_cost_per_request=0.0,
                success_rate=0.0
            )

# Instancia global del tracker
cost_tracker = CostTracker()
