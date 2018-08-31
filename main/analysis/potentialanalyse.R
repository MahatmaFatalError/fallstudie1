library('RPostgreSQL')
#install.packages("DMwR")
library(DMwR)
library(dplyr)


## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## dtab = dbReadTable(con, "restaurant")
dtab = dbGetQuery(con, "select  
                  city, 
                  avg(rating) avg_rating,
                  count(id) / max(size_sqkm) restaurants_per_sqkm,
                  sum(review_count)/ max(size_sqkm) reviewcounts_per_sqkm,
                  percentile_cont(0.5) within group (order by rating ) median,
                  min(rating), max(rating), mode() WITHIN GROUP (ORDER BY rating), stddev(rating) stddev,
                  sum(review_count) sum_review_count,
                  sum(review_count) / count(id) reviewcounts_per_restaurant,
                  max(buying_power) bp,
                  max(size_sqkm) size_sqkm,
                  max(population_sqkm) population_sqkm
                  from restaurants_in_germany
                  where review_count >= 9
                  group by city
                  having sum(review_count)  > 138")
summary(dtab)
str(dtab)

dtab$z_restaurants_per_sqkm <- SoftMax(dtab$restaurants_per_sqkm)
dtab$z_reviewcounts_per_restaurant <- SoftMax(dtab$reviewcounts_per_restaurant)
dtab$z_avg_rating <- SoftMax(dtab$avg_rating)
dtab$z_population_sqkm <- SoftMax(dtab$population_sqkm)

#dtab$potential <- (0.2 * dtab$z_restaurants_per_sqkm) * (0.2 * dtab$z_reviewcounts_per_restaurant) * (0.6 * dtab$z_avg_rating)
dtab$potential <- dtab$z_population_sqkm * (1-dtab$z_restaurants_per_sqkm) * (dtab$z_reviewcounts_per_restaurant) * (dtab$z_avg_rating)

View(arrange(dtab, desc(potential)))


# disconnect from the database
dbDisconnect(con)
