library(RPostgreSQL)

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

dbquery = dbGetQuery(con, "select * from restaurants_in_germany")
summary(dbquery)
str(dbquery)

# Parallism
# process in parallel
library(doParallel) 
cl <- makeCluster(detectCores(), type='PSOCK')
registerDoParallel(cl)

# turn parallel processing off and run sequentially again:
registerDoSEQ()

# Table in Data Frame
library(tibble)
dbquery_tbl <- as_data_frame(dbquery)
dbquery_tbl

library(Unicode)

dbquery_tbl$id <- NULL
dbquery_tbl$name <- NULL
# dbquery_tbl$price_range unicode
dbquery_tbl$price_range <- u_case_fold(dbquery_tbl$price_range)
# dbquery_tbl$price_range wenn NA dann €€
dbquery_tbl$price_range[is.na(dbquery_tbl$price_range)] <- "€€"
# dbquery_tbl$price_range zeiche z?hlen
dbquery_tbl$price_range <- nchar(dbquery_tbl$price_range)
# dbquery_tbl$city unicode
#dbquery_tbl$city <- u_case_fold(dbquery_tbl$city)
dbquery_tbl$city <- NULL
# dbquery_tbl$state
dbquery_tbl$state <- NULL
# #dbquery_tbl$category
#dbquery_tbl$category <- dbquery_tbl$category["Cafes"]
dbquery_tbl$category <- NULL
dbquery_tbl$population_sqkm[is.na(dbquery_tbl$population_sqkm)] <- median(dbquery_tbl$population_sqkm, na.rm=TRUE)
dbquery_tbl$buying_power[is.na(dbquery_tbl$buying_power)] <- median(dbquery_tbl$buying_power, na.rm=TRUE)
dbquery_tbl$rent_avg[is.na(dbquery_tbl$rent_avg)] <- median(dbquery_tbl$rent_avg, na.rm=TRUE)
head(dbquery_tbl)


fit.pe <- cor(dbquery_tbl, use="complete.obs",method="pearson")
fit.pe

library(corrplot)
M <- cor(dbquery_tbl)
corrplot(M, method = "circle") # in corrplot package, named "circle", "square", "ellipse", "number", "shade", "color", "pie".

metric

# compress Data

# Distanzma?
library(cluster)
fit.agn <- agnes(dbquery_tbl, metric="manhatten")

library(vegan)
fit.clu <- hclust(dist(dbquery), method="single")


