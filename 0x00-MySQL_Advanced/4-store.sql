-- Write a SQL script that creates a trigger to decrease the quantity of an item after adding a new order.
-- Quantity in the table items can be negative.
-- Context: Updating multiple tables for one action from your application can cause issues like network disconnections,
-- crashes, etc. To keep your data in good shape, let MySQL handle it for you!

CREATE TRIGGER decrease_items_quantity AFTER INSERT ON orders
FOR EACH ROW
UPDATE items
SET quantity = quantity - NEW.number
WHERE name = NEW.item_name;
