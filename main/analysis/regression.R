library(RPostgreSQL)

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

dbquery = dbGetQuery(con, "select * from restaurants_in_germany")
summary(dbquery)
str(dbquery)

library(tibble)
dbquery_tbl <- as_data_frame(dbquery)
dbquery_tbl

library(Unicode)
dbquery_tbl$price_range <- u_case_fold(dbquery_tbl$price_range)

# Multivariate Analyse
library(foreign)
fit.lm <- lm(rating~price_range, data=dbquery_tbl) # Rating hat sig. negativen Zusammenhang auf Price_Range
summary(fit.lm)
plot(fit.lm)
# population_sqkm kategorisieren
dbquery_tbl$population_sqkm2 <- cut(dbquery_tbl$population_sqkm, breaks=c(0,1000,3000,5000))
table(dbquery_tbl$population_sqkm2)
fit.lm1 <- lm(review_count~price_range+dbquery_tbl$population_sqkm2, data=dbquery_tbl)
summary(fit.lm1)


# Logistische Regression
review <- dbquery_tbl$review_count>0
fit.lr <- glm(review~rating+price_range+population_sqkm+buying_power+rent_avg, data=dbquery_tbl, family="binomial")
fit.lr # Negativer Zusammenhang review und rent
summary(fit.lr)
