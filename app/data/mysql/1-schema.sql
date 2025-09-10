-- Version inicial, falta revisar como se acomoda deacuerdo a la informacion que envian los chatbots


USE applestore_db;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('admin','user') DEFAULT 'user',
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla general de productos
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category ENUM('Iphone','Mac','Ipad','Watch','Accessories') NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    image_primary_url VARCHAR(255), -- Imagen principal
    image_secondary_url VARCHAR(255), -- Segunda imagen
    image_tertiary_url VARCHAR(255), -- Tercera imagen (NULL para accesorios)
    release_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===== TABLA ESPECÍFICA PARA iPHONES =====
CREATE TABLE IF NOT EXISTS iphones (
    id INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL, -- iPhone 15 Pro, iPhone 14, etc.
    generation INT NOT NULL, -- 15, 14, 13, etc.
    model_type ENUM('standard', 'Plus', 'Pro', 'Pro Max', 'SE') NOT NULL,
    storage_options JSON, -- ["128GB", "256GB", "512GB", "1TB"]
    storage_gb INT NOT NULL, -- Storage principal del modelo
    colors JSON, -- ["Natural Titanium", "Blue Titanium", "White Titanium", "Black Titanium"]
    display_size DECIMAL(3,1) NOT NULL, -- 6.1, 6.7, etc.
    display_technology VARCHAR(50), -- Super Retina XDR, Liquid Retina, etc.
    display_resolution VARCHAR(30), -- 2556×1179, etc.
    display_ppi INT, -- Pixels por pulgada
    chip VARCHAR(30) NOT NULL, -- A17 Pro, A16 Bionic, etc.
    cameras JSON, -- {"main": "48MP", "ultra_wide": "12MP", "telephoto": "12MP"}
    camera_features JSON, -- ["Night mode", "Portrait mode", "4K video", "Action mode"]
    front_camera VARCHAR(20), -- 12MP TrueDepth
    battery_video_hours INT, -- Horas de reproducción de video
    fast_charging BOOLEAN DEFAULT TRUE,
    wireless_charging BOOLEAN DEFAULT TRUE,
    magsafe_compatible BOOLEAN DEFAULT TRUE,
    water_resistance VARCHAR(10), -- IP68, IP67
    connectivity JSON, -- ["5G", "WiFi 6E", "Bluetooth 5.3", "USB-C", "Lightning"]
    face_id BOOLEAN DEFAULT TRUE,
    touch_id BOOLEAN DEFAULT FALSE,
    operating_system VARCHAR(20) DEFAULT 'iOS 17',
    height_mm DECIMAL(5,2), -- Alto en mm
    width_mm DECIMAL(5,2), -- Ancho en mm
    depth_mm DECIMAL(4,2), -- Grosor en mm
    weight_grams INT, -- Peso en gramos
    box_contents JSON, -- ["iPhone", "USB-C to Lightning Cable", "Documentation"]
    FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
);

-- ===== TABLA ESPECÍFICA PARA MAC =====
CREATE TABLE IF NOT EXISTS macs (
    id INT PRIMARY KEY,
    product_line ENUM('MacBook Air', 'MacBook Pro', 'iMac', 'Mac Studio', 'Mac Pro', 'Mac mini') NOT NULL,
    screen_size DECIMAL(4,1), -- 13.6, 14, 16, 24, etc. (NULL para Mac mini, Studio, Pro)
    chip VARCHAR(30) NOT NULL, -- M3, M3 Pro, M3 Max, M2, M1, Intel i7, etc.
    chip_cores JSON, -- {"cpu": 8, "gpu": 10, "neural": 16}
    ram_gb JSON, -- [8, 16, 24, 32, 64, 128] opciones disponibles
    ram_gb_base INT NOT NULL, -- RAM base del modelo
    ram_type VARCHAR(20), -- Unified Memory, DDR4, etc.
    storage_options JSON, -- ["256GB", "512GB", "1TB", "2TB", "4TB", "8TB"]
    storage_gb INT NOT NULL, -- Storage base
    storage_type VARCHAR(30), -- SSD, Fusion Drive, etc.
    display_technology VARCHAR(50), -- Liquid Retina, Retina, Studio Display, etc.
    display_resolution VARCHAR(30), -- 2560×1664, 3024×1964, etc.
    display_ppi INT, -- Pixels por pulgada
    display_brightness_nits INT, -- 500, 600, 1000, 1600 nits
    display_features JSON, -- ["P3 wide color", "True Tone", "ProMotion"]
    ports JSON, -- ["2x Thunderbolt", "MagSafe 3", "3.5mm headphone", "HDMI", "USB-A"]
    keyboard_type VARCHAR(30), -- Magic Keyboard, Touch Bar, etc.
    touch_bar BOOLEAN DEFAULT FALSE,
    touch_id BOOLEAN DEFAULT TRUE,
    webcam VARCHAR(20), -- 1080p FaceTime HD, Center Stage, etc.
    audio_features JSON, -- ["Four-speaker system", "Spatial Audio", "Studio-quality mics"]
    wireless JSON, -- ["Wi-Fi 6E", "Bluetooth 5.3"]
    operating_system VARCHAR(20) DEFAULT 'macOS Sonoma',
    battery_hours INT, -- Horas de batería (NULL para modelos de escritorio)
    height_mm DECIMAL(6,2), -- Alto en mm
    width_mm DECIMAL(6,2), -- Ancho en mm
    depth_mm DECIMAL(5,2), -- Grosor en mm
    weight_kg DECIMAL(4,2), -- Peso en kg
    colors JSON, -- ["Space Gray", "Silver", "Gold", "Midnight", "Starlight"]
    target_audience ENUM('Consumer', 'Pro', 'Studio') DEFAULT 'Consumer',
    FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
);

-- ===== TABLA ESPECÍFICA PARA iPAD =====
CREATE TABLE IF NOT EXISTS ipads (
    id INT PRIMARY KEY,
    product_line ENUM('iPad Pro', 'iPad Air', 'iPad', 'iPad mini') NOT NULL,
    generation INT, -- 6th generation, 5th generation, etc.
    screen_size DECIMAL(4,1) NOT NULL, -- 12.9, 11, 10.9, 8.3
    display_technology VARCHAR(50), -- Liquid Retina XDR, Liquid Retina, Retina
    display_resolution VARCHAR(30), -- 2732×2048, 2360×1640, etc.
    display_ppi INT,
    display_brightness_nits INT,
    display_features JSON, -- ["ProMotion", "P3 wide color", "True Tone", "Fully laminated"]
    chip VARCHAR(30) NOT NULL, -- M2, A16 Bionic, A15 Bionic, etc.
    storage_options JSON, -- ["64GB", "256GB", "512GB", "1TB", "2TB"]
    storage_gb INT NOT NULL,
    connectivity_options JSON, -- ["Wi-Fi", "Wi-Fi + Cellular"]
    cellular_support BOOLEAN DEFAULT FALSE,
    cellular_bands JSON, -- ["5G", "LTE", "eSIM"]
    cameras JSON, -- {"rear": "12MP Wide", "front": "12MP Ultra Wide"}
    camera_features JSON, -- ["4K video", "Center Stage", "Portrait mode"]
    apple_pencil_support ENUM('None', '1st gen', '2nd gen', 'USB-C') DEFAULT 'None',
    magic_keyboard_support BOOLEAN DEFAULT FALSE,
    smart_connector BOOLEAN DEFAULT FALSE,
    ports JSON, -- ["USB-C", "Lightning", "Smart Connector"]
    audio_features JSON, -- ["Stereo speakers", "Four speakers", "Studio-quality mics"]
    touch_id BOOLEAN DEFAULT TRUE,
    face_id BOOLEAN DEFAULT FALSE,
    operating_system VARCHAR(20) DEFAULT 'iPadOS 17',
    battery_hours INT, -- Horas de uso
    height_mm DECIMAL(6,2),
    width_mm DECIMAL(6,2),
    depth_mm DECIMAL(4,2),
    weight_grams INT,
    colors JSON, -- ["Space Gray", "Silver", "Pink", "Blue", "Purple"]
    FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
);

-- ===== TABLA ESPECÍFICA PARA APPLE WATCH =====
CREATE TABLE IF NOT EXISTS apple_watches (
    id INT PRIMARY KEY,
    series INT NOT NULL, -- 9, SE, Ultra 2, etc.
    model_type ENUM('Standard', 'SE', 'Ultra', 'Nike', 'Hermès') NOT NULL,
    case_sizes JSON, -- ["41mm", "45mm"] or ["49mm"] for Ultra
    case_size_mm INT NOT NULL, -- Tamaño base
    case_materials JSON, -- ["Aluminum", "Stainless Steel", "Titanium"]
    case_material VARCHAR(30) NOT NULL, -- Material base
    display_technology VARCHAR(50), -- Always-On Retina, Retina
    display_size_sq_mm INT, -- Área de pantalla en mm²
    display_brightness_nits INT,
    display_features JSON, -- ["Always-On", "ECG", "Blood Oxygen"]
    chip VARCHAR(20), -- S9, S8, etc.
    storage_gb INT DEFAULT 32,
    connectivity JSON, -- ["GPS", "Cellular", "Wi-Fi", "Bluetooth"]
    cellular_support BOOLEAN DEFAULT FALSE,
    health_sensors JSON, -- ["Heart Rate", "ECG", "Blood Oxygen", "Temperature"]
    fitness_features JSON, -- ["Workout Detection", "Fall Detection", "Crash Detection"]
    crown_type ENUM('Digital Crown', 'Digital Crown with haptic feedback') DEFAULT 'Digital Crown with haptic feedback',
    buttons JSON, -- ["Digital Crown", "Side Button", "Action Button"]
    water_resistance VARCHAR(20), -- "50 meters", "100 meters"
    operating_system VARCHAR(20) DEFAULT 'watchOS 10',
    battery_hours INT, -- Horas de batería
    fast_charging BOOLEAN DEFAULT TRUE,
    charging_method VARCHAR(30), -- "Magnetic Charging", "Fast Charging USB-C"
    band_compatibility JSON, -- ["All Apple Watch bands", "Specific sizes"]
    height_mm DECIMAL(4,1),
    width_mm DECIMAL(4,1),
    depth_mm DECIMAL(4,1),
    weight_grams DECIMAL(4,1),
    colors JSON, -- ["Midnight", "Starlight", "Silver", "Gold", "Graphite"]
    target_audience ENUM('Everyday', 'Fitness', 'Adventure', 'Luxury') DEFAULT 'Everyday',
    FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
);

-- ===== TABLA ESPECÍFICA PARA ACCESORIOS =====
CREATE TABLE IF NOT EXISTS accessories (
    id INT PRIMARY KEY,
    accessory_type ENUM('Audio', 'Charging', 'Input', 'Storage', 'Protection', 'Connectivity', 'Software') NOT NULL,
    category VARCHAR(50) NOT NULL, -- AirPods, Cables, Keyboards, Cases, etc.
    compatibility JSON, -- ["iPhone 15", "iPhone 14", "All Lightning devices"]
    wireless_technology VARCHAR(30), -- Bluetooth 5.3, Wi-Fi 6, etc.
    connectivity JSON, -- ["Lightning", "USB-C", "3.5mm", "Wireless"]
    battery_hours INT, -- Para productos con batería
    charging_case_hours INT, -- Horas adicionales del case (AirPods)
    fast_charging BOOLEAN DEFAULT FALSE,
    noise_cancellation BOOLEAN DEFAULT FALSE,
    water_resistance VARCHAR(10), -- IPX4, IP68, etc.
    materials JSON, -- ["Aluminum", "Plastic", "Leather", "Silicone"]
    colors JSON,
    dimensions_mm VARCHAR(50), -- "21.7 x 18.1 x 24.0 mm"
    weight_grams DECIMAL(5,1),
    special_features JSON, -- ["Spatial Audio", "Adaptive Transparency", "MagSafe"]
    included_accessories JSON, -- ["Charging Case", "Lightning Cable", "Documentation"]
    operating_system_req VARCHAR(50), -- "iOS 16.1 or later"
    FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Tabla intermedia: productos por venta
CREATE TABLE IF NOT EXISTS sales_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Tabla de chats (una conversación)
CREATE TABLE IF NOT EXISTS chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    source ENUM('web','whatsapp','telegram') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Tabla de mensajes (historial de cada chat)
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender ENUM('user','bot') NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);