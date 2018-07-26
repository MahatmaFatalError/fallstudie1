
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## dtab = dbReadTable(con, "restaurant")
dtab = dbGetQuery(con, "select * from restaurants_final")
summary(dtab)
str(dtab)




## crunch character data to factors
priceCat = factor(dtab$price_range)
#str(priceCat)
#levels(priceCat)
dtab$price_range = priceCat

foodCat = factor(dtab$category)
#str(foodCat)
#levels(foodCat)
dtab$category = foodCat

dtab$category1 = factor(dtab$category1)
dtab$category2 = factor(dtab$category2)
dtab$category3 = factor(dtab$category3)

cityCat = factor(dtab$city)
dtab$city = cityCat
stateCat = factor(dtab$state)
dtab$state = stateCat

## linear Regression
#fit.lr <- lm(rating ~ price_range + state + review_count + buying_power + population_sqkm + category, data=dtab )
fit.lr <- lm(cbind(price_range,state,review_count,buying_power,
                   population_sqkm, category) ~ rating, data=dtab )
summary(fit.lr)

## tree
library(partykit)
fit.t <- ctree(rating ~ price_range + state + review_count + buying_power + population_sqkm, data=dtab)
plot(fit.t)


library(effects)
plot(effect("price_range", fit.lr))
plot(effect("category", fit.lr))
plot(effect("state", fit.lr))
plot(effect("buying_power", fit.lr))
plot(effect("population_sqkm", fit.lr))


# disconnect from the database
dbDisconnect(con)
