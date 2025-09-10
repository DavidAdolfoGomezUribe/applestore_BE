-- Datos iniciales para AppleStore

-- Usuarios (4: 2 admins, 2 users)
INSERT INTO users (role, name, email, password) VALUES
('admin', 'Ana Admin', 'ana.admin@example.com', 'adminpass1'),
('admin', 'Carlos Admin', 'carlos.admin@example.com', 'adminpass2'),
('user', 'Beatriz User', 'beatriz.user@example.com', 'userpass1'),
('user', 'David User', 'david.user@example.com', 'userpass2');

-- 20 productos
INSERT INTO products (category, name, description, price, stock, image_url) VALUES
('Iphone', 'iPhone 15 Pro', 'El último iPhone con chip A17', 1299.99, 10, 'https://example.com/iphone15pro.jpg'),
('Iphone', 'iPhone 14', 'iPhone generación anterior', 999.99, 15, 'https://example.com/iphone14.jpg'),
('Iphone', 'iPhone SE', 'iPhone compacto y económico', 499.99, 20, 'https://example.com/iphonese.jpg'),
('Mac', 'MacBook Pro M2', 'Potente portátil para profesionales', 1999.99, 8, 'https://example.com/macbookprom2.jpg'),
('Mac', 'MacBook Air M1', 'Ligero y eficiente', 1099.99, 12, 'https://example.com/macbookairm1.jpg'),
('Mac', 'iMac 24"', 'Todo en uno con pantalla Retina', 1599.99, 5, 'https://example.com/imac24.jpg'),
('Ipad', 'iPad Pro 12.9"', 'iPad profesional con pantalla grande', 1299.99, 7, 'https://example.com/ipadpro12.jpg'),
('Ipad', 'iPad Air', 'iPad ligero y potente', 799.99, 10, 'https://example.com/ipadair.jpg'),
('Ipad', 'iPad Mini', 'iPad compacto', 599.99, 9, 'https://example.com/ipadmini.jpg'),
('Watch', 'Apple Watch Series 9', 'Última generación de Apple Watch', 499.99, 18, 'https://example.com/watch9.jpg'),
('Watch', 'Apple Watch SE', 'Apple Watch económico', 299.99, 20, 'https://example.com/watchse.jpg'),
('Accesories', 'AirPods Pro', 'Auriculares inalámbricos con cancelación de ruido', 249.99, 25, 'https://example.com/airpodspro.jpg'),
('Accesories', 'AirPods 3', 'Auriculares inalámbricos', 179.99, 30, 'https://example.com/airpods3.jpg'),
('Accesories', 'Magic Mouse', 'Ratón inalámbrico', 99.99, 15, 'https://example.com/magicmouse.jpg'),
('Accesories', 'Magic Keyboard', 'Teclado inalámbrico', 129.99, 14, 'https://example.com/magickeyboard.jpg'),
('Accesories', 'Apple Pencil 2', 'Lápiz para iPad', 129.99, 16, 'https://example.com/applepencil2.jpg'),
('Accesories', 'Smart Folio', 'Funda para iPad', 89.99, 22, 'https://example.com/smartfolio.jpg'),
('Accesories', 'USB-C Adapter', 'Adaptador USB-C', 39.99, 40, 'https://example.com/usbcadapter.jpg'),
('Accesories', 'MagSafe Charger', 'Cargador inalámbrico', 49.99, 35, 'https://example.com/magsafecharger.jpg'),
('Accesories', 'AppleCare+', 'Seguro extendido para productos Apple', 199.99, 50, 'https://example.com/applecare.jpg');

-- 4 ventas (mezclando productos y usuarios)
INSERT INTO sales (user_id, total) VALUES
(1, 2599.98), -- Ana Admin
(2, 2299.97), -- Carlos Admin
(3, 1249.96),  -- Beatriz User
(4, 2399.96); -- David User

-- Productos por venta (sales_products)
-- Venta 1: Ana Admin compra 2 iPhone 15 Pro
INSERT INTO sales_products (sale_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 2, 1299.99, 2599.98),
-- Venta 2: Carlos Admin compra 1 MacBook Pro M2 y 1 iPad Pro 12.9"
(2, 4, 1, 1999.99, 1999.99),
(2, 7, 1, 1299.99, 1299.99),
-- Venta 3: Beatriz User compra 2 Apple Watch Series 9 y 2 AirPods Pro
(3, 10, 2, 499.99, 999.98),
(3, 12, 2, 249.99, 499.98),
-- Venta 4: David User compra 2 MacBook Air M1 y 2 Magic Mouse
(4, 5, 2, 1099.99, 2199.98),
(4, 14, 2, 99.99, 199.98);
