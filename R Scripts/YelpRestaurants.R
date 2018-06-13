
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## dtab = dbReadTable(con, "restaurant")
dtab = dbGetQuery(con, "select * from restaurant where is_closed = false")
summary(dtab)
str(dtab)

## crunch data
priceCat = factor(dtab$price_range)
str(priceCat)
levels(priceCat)
dtab$price_range = priceCat

## linear Regression
fit.lr <- lm(rating ~ price_range + longitude + latitude + review_count,
              data=dtab )
summary(fit.lr)

## tree
library(partykit)
fit.t <- ctree(rating ~ price_range + review_count, data=dtab)
plot(fit.t)


library(effects)
plot(effect("price_range", fit.lr))
