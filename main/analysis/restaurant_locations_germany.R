
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## create view restaurants_in_germany as (
##  select r.*, c.name as category from restaurant r inner join food_category c on r.id = c.restaurant_id
##  where city is not null)

## dtab = dbReadTable(con, "restaurant")
dtab = dbGetQuery(con, "select * from restaurants_in_germany where is_closed = false")
summary(dtab)
str(dtab)

## crunch character data to factors
priceCat = factor(dtab$price_range)
str(priceCat)
levels(priceCat)
dtab$price_range = priceCat

foodCat = factor(dtab$category)
str(foodCat)
levels(foodCat)
dtab$category = foodCat

cityCat = factor(dtab$city)
dtab$city = cityCat
stateCat = factor(dtab$state)
dtab$state = stateCat

## linear Regression
fit.lr <- lm(rating ~ city + state + review_count + category , data=dtab ) #+ price_range
summary(fit.lr)

## tree
library(partykit)
fit.t <- ctree(rating ~ price_range + city + review_count + category, data=dtab)
plot(fit.t)


library(effects)
plot(effect("price_range", fit.lr))


# disconnect from the database
dbDisconnect(con)
