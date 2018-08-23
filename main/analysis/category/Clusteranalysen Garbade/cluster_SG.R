
## library('RPostgreSQL')

## ## connect to db
## pg = dbDriver("PostgreSQL")
## con = dbConnect(pg, user="postgres", password="team123",
##                 host="35.190.205.207", port=5432, dbname="fonethd")

## ## dtab = dbReadTable(con, "restaurant")
## dtab = dbGetQuery(con, "select * from restaurants_final")

## BEGINN SG
dtab <- read.csv("restaurants_categories_flat_temp_201807270817.csv")

dtab$cat1 <- replace(dtab$cat1, dtab$cat1=="", NA)
dtab$cat2 <- replace(dtab$cat2, dtab$cat2=="", NA)
dtab$cat3 <- replace(dtab$cat3, dtab$cat3=="", NA)

d <- dtab[,-1]
d <- na.omit(d)

require(cluster)
gower.dist <- daisy(d, metric = c("gower"))

require(cluster)
fit1 <- agnes(gower.dist, method="ward") 
fit2 <- agnes(gower.dist, method="average") 
fit3 <- agnes(gower.dist, method="single") 
fit4 <- agnes(gower.dist, method="complete")

## Dendrgramm mit
plot(fit1, which=2)
x11(); plot(fit2, which=2)
x11(); plot(fit3, which=2)
x11(); plot(fit4, which=2)

## END SG

summary(dtab)
str(dtab)

## crunch character data to factors
dtab$category1 = factor(dtab$category1)
dtab$category2 = factor(dtab$category2)
dtab$category3 = factor(dtab$category3)

categoriesToCluster <- dtab[,12:14]

require(cluster)
#fit1 <- agnes(categoriesToCluster, method="ward") 
#fit2 <- agnes(categoriesToCluster, method="average") 
#fit3 <- agnes(categoriesToCluster, method="single") 
#fit4 <- agnes(categoriesToCluster, method="complete")

# https://medium.com/@anastasia.reusova/hierarchical-clustering-on-categorical-data-in-r-a27e578f2995
gower.dist <- daisy(categoriesToCluster, metric = c("gower")) ## memory limitation

divisive.clust <- diana(as.matrix(gower.dist), 
                        diss = TRUE, keep.diss = TRUE)
plot(divisive.clust, main = "Divisive")

aggl.clust.c <- hclust(gower.dist, method = "complete")
plot(aggl.clust.c,
     main = "Agglomerative, complete linkages")



# https://dabblingwithdata.wordpress.com/2016/10/10/clustering-categorical-data-with-r/

install.packages("klaR")
library(klaR)
cluster.results <-kmodes(categoriesToCluster, 6, iter.max = 10, weighted = FALSE ) ## Fehler in x[[jj]][iseq] <- vjj : Ersetzung hat Länge 0

install.packages("cba")
library(cba)
cluster.results <-rockCluster(as.matrix(categoriesToCluster), 6 ) ## whole R session crashes
cluster.output <- cbind(categoriesToCluster,cluster.results$cl)


# disconnect from the database
dbDisconnect(con)
