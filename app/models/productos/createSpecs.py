import json

def create_iphone_spec(conn, product_id, spec):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO iphones (
            id, model, generation, model_type, storage_options, storage_gb, colors, display_size, display_technology, display_resolution, display_ppi, chip, cameras, camera_features, front_camera, battery_video_hours, fast_charging, wireless_charging, magsafe_compatible, water_resistance, connectivity, face_id, touch_id, operating_system, height_mm, width_mm, depth_mm, weight_grams, box_contents
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_id,
            spec.model,
            spec.generation,
            spec.model_type,
            json.dumps(spec.storage_options),
            spec.storage_gb,
            json.dumps(spec.colors),
            spec.display_size,
            spec.display_technology,
            spec.display_resolution,
            spec.display_ppi,
            spec.chip,
            json.dumps(spec.cameras),
            json.dumps(spec.camera_features),
            spec.front_camera,
            spec.battery_video_hours,
            spec.fast_charging,
            spec.wireless_charging,
            spec.magsafe_compatible,
            spec.water_resistance,
            json.dumps(spec.connectivity),
            spec.face_id,
            spec.touch_id,
            spec.operating_system,
            spec.height_mm,
            spec.width_mm,
            spec.depth_mm,
            spec.weight_grams,
            json.dumps(spec.box_contents)
        )
    )
    conn.commit()

def create_mac_spec(conn, product_id, spec):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO macs (
            id, product_line, screen_size, chip, chip_cores, ram_gb, ram_gb_base, ram_type, storage_options, storage_gb, storage_type, display_technology, display_resolution, display_ppi, display_brightness_nits, display_features, ports, keyboard_type, touch_bar, touch_id, webcam, audio_features, wireless, operating_system, battery_hours, height_mm, width_mm, depth_mm, weight_kg, colors, target_audience
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_id,
            spec.product_line,
            spec.screen_size,
            spec.chip,
            json.dumps(spec.chip_cores),
            json.dumps(spec.ram_gb),
            spec.ram_gb_base,
            spec.ram_type,
            json.dumps(spec.storage_options),
            spec.storage_gb,
            spec.storage_type,
            spec.display_technology,
            spec.display_resolution,
            spec.display_ppi,
            spec.display_brightness_nits,
            json.dumps(spec.display_features),
            json.dumps(spec.ports),
            spec.keyboard_type,
            spec.touch_bar,
            spec.touch_id,
            spec.webcam,
            json.dumps(spec.audio_features),
            json.dumps(spec.wireless),
            spec.operating_system,
            spec.battery_hours,
            spec.height_mm,
            spec.width_mm,
            spec.depth_mm,
            spec.weight_kg,
            json.dumps(spec.colors),
            spec.target_audience
        )
    )
    conn.commit()

def create_ipad_spec(conn, product_id, spec):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ipads (
            id, product_line, generation, screen_size, display_technology, display_resolution, display_ppi, display_brightness_nits, display_features, chip, storage_options, storage_gb, connectivity_options, cellular_support, cellular_bands, cameras, camera_features, apple_pencil_support, magic_keyboard_support, smart_connector, ports, audio_features, touch_id, face_id, operating_system, battery_hours, height_mm, width_mm, depth_mm, weight_grams, colors
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_id,
            spec.product_line,
            spec.generation,
            spec.screen_size,
            spec.display_technology,
            spec.display_resolution,
            spec.display_ppi,
            spec.display_brightness_nits,
            json.dumps(spec.display_features),
            spec.chip,
            json.dumps(spec.storage_options),
            spec.storage_gb,
            json.dumps(spec.connectivity_options),
            spec.cellular_support,
            json.dumps(spec.cellular_bands),
            json.dumps(spec.cameras),
            json.dumps(spec.camera_features),
            spec.apple_pencil_support,
            spec.magic_keyboard_support,
            spec.smart_connector,
            json.dumps(spec.ports),
            json.dumps(spec.audio_features),
            spec.touch_id,
            spec.face_id,
            spec.operating_system,
            spec.battery_hours,
            spec.height_mm,
            spec.width_mm,
            spec.depth_mm,
            spec.weight_grams,
            json.dumps(spec.colors)
        )
    )
    conn.commit()

def create_apple_watch_spec(conn, product_id, spec):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO apple_watches (
            id, series, model_type, case_sizes, case_size_mm, case_materials, case_material, display_technology, display_size_sq_mm, display_brightness_nits, display_features, chip, storage_gb, connectivity, cellular_support, health_sensors, fitness_features, crown_type, buttons, water_resistance, operating_system, battery_hours, fast_charging, charging_method, band_compatibility, height_mm, width_mm, depth_mm, weight_grams, colors, target_audience
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_id,
            spec.series,
            spec.model_type,
            json.dumps(spec.case_sizes),
            spec.case_size_mm,
            json.dumps(spec.case_materials),
            spec.case_material,
            spec.display_technology,
            spec.display_size_sq_mm,
            spec.display_brightness_nits,
            json.dumps(spec.display_features),
            spec.chip,
            spec.storage_gb,
            json.dumps(spec.connectivity),
            spec.cellular_support,
            json.dumps(spec.health_sensors),
            json.dumps(spec.fitness_features),
            spec.crown_type,
            json.dumps(spec.buttons),
            spec.water_resistance,
            spec.operating_system,
            spec.battery_hours,
            spec.fast_charging,
            spec.charging_method,
            json.dumps(spec.band_compatibility),
            spec.height_mm,
            spec.width_mm,
            spec.depth_mm,
            spec.weight_grams,
            json.dumps(spec.colors),
            spec.target_audience
        )
    )
    conn.commit()

def create_accessory_spec(conn, product_id, spec):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO accessories (
            id, accessory_type, category, compatibility, wireless_technology, connectivity, battery_hours, charging_case_hours, fast_charging, noise_cancellation, water_resistance, materials, colors, dimensions_mm, weight_grams, special_features, included_accessories, operating_system_req
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_id,
            spec.accessory_type,
            spec.category,
            json.dumps(spec.compatibility),
            spec.wireless_technology,
            json.dumps(spec.connectivity),
            spec.battery_hours,
            spec.charging_case_hours,
            spec.fast_charging,
            spec.noise_cancellation,
            spec.water_resistance,
            json.dumps(spec.materials),
            json.dumps(spec.colors),
            spec.dimensions_mm,
            spec.weight_grams,
            json.dumps(spec.special_features),
            json.dumps(spec.included_accessories),
            spec.operating_system_req
        )
    )
    conn.commit()
