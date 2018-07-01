CREATE OR REPLACE VIEW public.restaurants_in_germany AS
 SELECT r.id,
    r.name,
    r.rating,
    r.price_range,
    r.review_count,
    r.city,
    r.state,
    c.name AS category,
    city.population_sqkm,
    city.buying_power,
    city.rent_avg
   FROM restaurant r
     JOIN ( SELECT food_category.restaurant_id,
            array_agg(food_category.name) AS name
           FROM food_category
          GROUP BY food_category.restaurant_id) c ON r.id::text = c.restaurant_id::text
     JOIN city ON r.city::text = city.name::text
     JOIN zip_code ON city.id = zip_code.city_id
  WHERE r.city IS NOT NULL AND r.zip_code = zip_code.zip_code AND r.is_closed = false;
