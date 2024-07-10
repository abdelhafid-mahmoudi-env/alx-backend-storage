-- 3-glam_rock.sql
SELECT band_name, (2022 - formed) AS lifespan
FROM metal_bands
WHERE style = 'Glam rock'
ORDER BY lifespan DESC;
