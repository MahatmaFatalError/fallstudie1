
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
hist(restaurants_final$review_count)
boxplot(restaurants_final$review_count)
summary(restaurants_final$review_count)

# categorize buying power into opgroups
dtab$buying_power_groups <- cut(dtab$buying_power, breaks=c(-Inf, 20000, 24000, 28000, Inf), labels=c("low","middle", "upper middle","high"))
plot(dtab$buying_power_groups)


## crunch character data to factors
restaurants_final$price_range = factor(restaurants_final$price_range)


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
fit.t <- ctree(rating ~ price_range + review_count + state + population_sqkm + buying_power, data=restaurants_final)
plot(fit.t)


library(caret)
model2 <- train(rating ~ price_range + review_count + state + population_sqkm + buying_power , data = restaurants_final, method='ctree', tuneLength=2
               #, trControl=trainControl(method='cv', number=10, classProbs=TRUE, summaryFunction=twoClassSummary)
               )
model2
plot(model2)


# kommt zu keinem Ende
#fit.rf <- cforest(rating ~ price_range + review_count + state + population_sqkm + buying_power, data=restaurants_final)
#plot(fit.rf)

library(rpart)
fit.cart <- rpart(rating ~ price_range + review_count + state + population_sqkm + buying_power, data=restaurants_final)
plot(fit.cart) #


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


# latex
install.packages("stargazer")
library(stargazer)

allecities= dbGetQuery(con, "select * from restaurants_in_germany")
großstadt = dbGetQuery(con, "select * from restaurants_in_germany where type = 'Großstadt'")
mittelstadt = dbGetQuery(con, "select * from restaurants_in_germany where type = 'Mittelstadt'")
kleinstadt = dbGetQuery(con, "select * from restaurants_in_germany where type = 'Kleinstadt'")
summary(großstadt$review_count)
summary(mittelstadt$review_count)
summary(kleinstadt$review_count)

boxplot(review_count~type, data=allecities)

summary(großstadt$review_count)

großstadt = dbGetQuery(con, "select * from restaurants_in_germany where type = 'Großstadt'")
summary(großstadt$review_count)
stargazer(restaurants_final)


stats = dbGetQuery(con, "select city, count(id) restaraunts, sum(review_count) review_counts from restaurants_in_germany group by city")
statsGroßstadt = dbGetQuery(con, "select city, count(id) restaraunts, sum(review_count) review_counts from restaurants_in_germany where type = 'Großstadt' group by city")
statsMittelstadt = dbGetQuery(con, "select city, count(id) restaraunts, sum(review_count) review_counts from restaurants_in_germany where type = 'Mittelstadt' group by city")
statsKleinstadt = dbGetQuery(con, "select city, count(id) restaraunts, sum(review_count) review_counts from restaurants_in_germany where type = 'Kleinstadt' group by city")
summary(stats)
summary(statsGroßstadt)
summary(statsMittelstadt)
summary(statsKleinstadt)


stargazer(stats)
summary(stats)
boxplot(stats$restaraunts)
boxplot(stats$review_counts)
histogram(stats$review_counts)

# disconnect from the database
dbDisconnect(con)
