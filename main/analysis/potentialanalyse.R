library('RPostgreSQL')
#install.packages("DMwR")
library(DMwR)
library(dplyr)
library(stringr)


## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

restaurantsPerCity = dbGetQuery(con, "select avg(rs), percentile_cont(0.5) within group (order by rs ) median from (
                  select city, count(review_count) rs
                  from restaurants_in_germany group by city) foo")


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
                  max(population_sqkm) population_sqkm,
                  max(state) state
                  from restaurants_in_germany
                  where review_count >= 9 and population_sqkm > 0
                  group by city
                  having sum(review_count)  > 138 and count(review_count) >= 28")

# Wertebereiche standardisieren
dtab$z_restaurants_per_sqkm <- SoftMax(dtab$restaurants_per_sqkm)
dtab$z_reviewcounts_per_restaurant <- SoftMax(dtab$reviewcounts_per_restaurant)
dtab$z_avg_rating <- SoftMax(dtab$avg_rating)
dtab$z_population_restaurants_sqkm <- SoftMax(dtab$population_sqkm / dtab$restaurants_per_sqkm)
#dtab$z_restaurants_population_sqkm <- SoftMax((dtab$restaurants_per_sqkm / dtab$population_sqkm))

dtab$potential <- (dtab$z_population_restaurants_sqkm) * (dtab$z_reviewcounts_per_restaurant) * (dtab$z_avg_rating)
# je höher z_population_restaurants_sqkm (also je mehr Einwohner/Restaurants) desto besser für unser potential
#TODO: genau die einzenlen faktoren begründen, warum keine weiteren faktoren?


View(arrange(dtab, desc(potential)))
insert <- arrange(dtab[, c(1, 12, 17)], desc(potential))
dbExecute(con, "TRUNCATE TABLE top_cities")
dbWriteTable(con, "top_cities", value = insert[1:100, ], row.names = FALSE, append = TRUE) #append = TRUE
dbExecute(con, "REFRESH MATERIALIZED VIEW categorie_frequency_materialized WITH DATA")
dbExecute(con, "REFRESH MATERIALIZED VIEW top10_city_category_2 WITH DATA;")

### korrelationskoeff buying power mit price range, scatter plot // -> keine nennenswerte korrelation
### durchschnitts rating pro PLZ von den städten ->  table top10_city_plz


# Kontingenzanalyse lokale kategorieverteilung vs globale verteilung  -> table top10_city_category
# für top10 cities
i = 0
while(i<10){
  i=i+1;
  # nur diejenigen globalen Kategorien berücksichtigen, die es auch lokal gibt
  global_distribution <- dbGetQuery(con, str_c("select l.city, g.* from categorie_frequency_materialized g, top10_city_category_2 l
            where g.cat in (l.cat) and l.city = '", insert$city[i] ,"' order by cat"))
  global_distribution$prozent <- global_distribution$freq/sum(global_distribution$freq)
  
  local_distribution <- dbGetQuery(con, str_c("select * from top10_city_category_2  where  city = '", insert$city[i] ,"' order by cat"))
  local_distribution$prozent <- local_distribution$counter/sum(local_distribution$counter)
  
  r <- chisq.test(local_distribution$counter, p=global_distribution$prozent)
  local_distribution$residuals <- r$residuals 
  
  # suche betraglich hohe negative Abweichung
  cat("\n")
  print(str_c(i, ". p-value:",r$p.value))
  print(subset(local_distribution, residuals <= -2))
}


# Globale Verleilung nun mit allen Kategorien
global_distribution <- dbGetQuery(con, str_c("select g.* from categorie_frequency_materialized g order by cat"))
global_distribution$prozent <- global_distribution$freq/sum(global_distribution$freq)
i = 0
while(i<10){
  i=i+1;
  local_distribution <- dbGetQuery(con, str_c("select * from top10_city_category_2  where  city = '", insert$city[i] ,"'
                                              union
                                              select '", insert$city[i] ,"', g.cat, 0 from categorie_frequency_materialized g where g.cat not in (select cat from top10_city_category_2  where  city = '", insert$city[i] ,"')
                                              order by cat"))
  local_distribution$prozent <- local_distribution$counter/sum(local_distribution$counter)
  
  r <- chisq.test(local_distribution$counter, p=global_distribution$prozent)
  local_distribution$residuals <- r$residuals 
  
  # suche betraglich hohe negative Abweichung
  cat("\n")
  print(str_c(i, ". p-value:",r$p.value))
  print(subset(local_distribution, residuals <= -2))
}


# disconnect from the database
dbDisconnect(con)
