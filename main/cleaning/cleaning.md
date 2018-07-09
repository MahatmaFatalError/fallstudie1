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
```

# 7. ```buying_power``` cleaning
Take a look at ```buying_power.py``` script.