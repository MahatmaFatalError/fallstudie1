# 1. ```review_count``` cleaning
```sql
UPDATE public.restaurant SET review_count = 0 WHERE review_count IS NULL;
```

# 2. Address cleaning
Take a look at ```address.py``` script.
<br>
After script execution:
```sql
DELETE FROM public.restaurant where city is null;
```
<b>Reason</b>:
<br>
Fetching these restaurants from yelp always resulted in a 404 or 403 HTTP Error.
<br>
--> Address could not be retrieved.

# 3. ```price_range``` cleaning
Take a look at ```price_range.py``` script.

# 4.  ```country``` cleaning
```sql
DELETE FROM public.restaurant WHERE country != 'DE'
```

## 4.1  "Frankfurt" harmonization
```sql
update restaurant set city = 'Frankfurt am Main'
where city = 'Frankfurt' and state = 'HE'

update restaurant set city = 'Frankfurt am Main'
where city = 'Frankfurt Am Main' and state = 'HE'
```

# 5.  ```street``` cleaning
Only a few restaurants have null values within attribute ```street```.
<br>
Leave them --> ```street``` is not really important for us.

# 6.  ```price_range_calculated``` Table cleaning
```sql
UPDATE public.price_range_calculated
	SET price_range = '€€'
	WHERE price_range = '-1';

UPDATE public.price_range_calculated
	SET price_range = '€€'
	WHERE price_range = '-2';

COALESCE(restaurant.price_range, pr.price_range) AS price_range_cleaned
 FROM restaurant
   LEFT JOIN price_range_calculated pr ON pr.restaurant_id::text = restaurant.id::text;
```

# 7. ```buying_power``` cleaning
Take a look at ```buying_power.py``` script.
```sql
COALESCE(city.buying_power, bp.buying_power) AS buying_power_cleaned
	FROM city
		LEFT JOIN buying_power_calculated bp ON bp.city_id = city.id;
```

# 8. ```rent_avg``` cleaning
Take a look at ```rent_avg.py``` script.

# 8. ```review_count``` cleaning
Take a look at ```review_count.py``` script.


# Top City Cleaning

```sql
UPDATE public.top_cities
	SET city='Hannover'
	WHERE city = 'Hanover';
```

1. Hanover
2. Dusseldorf
3. Nuremberg
4. Munich 
