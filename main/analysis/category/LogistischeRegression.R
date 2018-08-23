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

# Logistische Regression
review <- dbquery_tbl$review_count>0
fit.lr <- glm(review~rating+price_range+population_sqkm+buying_power+rent_avg, data=dbquery_tbl, family="binomial")
fit.lr # Negativer Zusammenhang review ud price_rang, buying_power
summary(fit.lr)
# daraus ergibt sich
# berechnung Lgits
logits <- -3.862+7.320*dbquery_tbl$rating-7.164*dbquery_tbl$price_range+2.144*dbquery_tbl$population_sqkm-7.354*dbquery_tbl$buying_power+4.486*dbquery_tbl$rent_avg
dbquery_tbl$Logits <- predict(fit.lr, date=dbquery_tbl)
dbquery_tbl$P <- predict(fit.lr, type="response", data=dbquery_tbl)
dbquery_tbl # Reviewwahrscheinlichkeit P
# McFadden-R²
LLo <- logLik(nullmod)
LLv <- logLik(fit.lr)
(fadden <- as.numeric(1-(LLv/LLo))) # 0.5033 # Modell ist also gut!

