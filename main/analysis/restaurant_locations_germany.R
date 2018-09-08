
#library(ggplot2)
#library(dplyr)
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## dtab = dbReadTable(con, "restaurant")
restaurants_final = dbGetQuery(con, "select * from restaurants_final")
summary(restaurants_final)
str(restaurants_final)
hist(dtab$buying_power)


# categorize buying power into opgroups
dtab$buying_power_groups <- cut(dtab$buying_power, breaks=c(-Inf, 20000, 24000, 28000, Inf), labels=c("low","middle", "upper middle","high"))
plot(dtab$buying_power_groups)


## crunch character data to factors
priceCat = factor(dtab$price_range)
#str(priceCat)
#levels(priceCat)
dtab$price_range = priceCat

foodCat = factor(dtab$category)
#str(foodCat)
#levels(foodCat)
dtab$category = foodCat

restaurants_final$category1 = factor(restaurants_final$category1)
restaurants_final$category2 = factor(restaurants_final$category2)
restaurants_final$category3 = factor(restaurants_final$category3)

cityCat = factor(dtab$city)
dtab$city = cityCat
restaurants_final$state = factor(restaurants_final$state)
plot(dtab$state)

## linear Regression
fit.lr <- lm(rating ~ price_range + review_count + state + population_sqkm + buying_power + category1 + category2 + category3, data=restaurants_final )
#fit.lr <- lm(cbind(price_range,state,review_count,buying_power, population_sqkm, rent_avg) ~ rating, data=dtab )
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

plot(dtab$review_count, dtab$rating)
plot(restaurants_final$rating , restaurants_final$buying_power)
plot(dtab$review_count, dtab$population_sqkm)


require(corrplot)
require(RColorBrewer)
corrplot(dtab, type = "full", order = "hclust")

# Beide sind normalverteilt, bedingung für pearson
shapiro.test(restaurants_final$rating[1:5000])
shapiro.test(restaurants_final$buying_power[1:5000])

# ganz leichte minimale negative signifikante korrelation
cor.test(restaurants_final$buying_power,restaurants_final$rating, method="pearson")

View(dtab)

# disconnect from the database
dbDisconnect(con)
