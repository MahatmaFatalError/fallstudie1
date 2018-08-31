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
                  stddev(rating) stddev,
                  sum(review_count) sum_review_count,
                  sum(review_count) / count(id) reviewcounts_per_restaurant,
                  max(buying_power) bp,
                  max(size_sqkm) size_sqkm,
                  max(population_sqkm) population_sqkm
                  from restaurants_in_germany
                  where review_count >= 9 and population_sqkm > 0
                  group by city
                  having sum(review_count)  > 138")
#summary(dtab)
#str(dtab)

dtab$z_restaurants_per_sqkm <- SoftMax(dtab$restaurants_per_sqkm)
dtab$z_reviewcounts_per_restaurant <- SoftMax(dtab$reviewcounts_per_restaurant)
dtab$z_avg_rating <- SoftMax(dtab$avg_rating)
dtab$z_population_restaurants_sqkm <- SoftMax(dtab$population_sqkm / dtab$restaurants_per_sqkm)
#dtab$z_restaurants_population_sqkm <- SoftMax((dtab$restaurants_per_sqkm / dtab$population_sqkm))
#((dtab$restaurants_per_sqkm / dtab$population_sqkm)) 

#dtab$potential <- (0.2 * dtab$z_restaurants_per_sqkm) * (0.2 * dtab$z_reviewcounts_per_restaurant) * (0.6 * dtab$z_avg_rating)
dtab$potential <- (dtab$z_population_restaurants_sqkm) * (dtab$z_reviewcounts_per_restaurant) * (dtab$z_avg_rating)
# je höher z_population_restaurants_sqkm (also je mehr Einwohner/Restaurants) desto besser für unser potential

View(arrange(dtab, desc(potential)))
insert <- arrange(dtab[0:100, c(1, 16)], desc(potential))
dbWriteTable(con, "top_cities", value = insert, row.names = FALSE) #append = TRUE

# effect buying power mit price range, scatter plot // -> keine nennenswerte korrelation
# TODO: Kontingenzanalyse chi^2 test lokale kategorieverteilung vs globale verteilung  -> top10_city_category
# durchschnitts rating pro PLZ von den städten ->  top10_city_plz

# disconnect from the database
dbDisconnect(con)
