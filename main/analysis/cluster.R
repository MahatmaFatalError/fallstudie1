
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

##### hclust for binary matrix

data = dbGetQuery(con, "select * from restaurants_categories_flatter") # 68.734 rows
summary(data)

categoriesToCluster <- data[,-1]   # get rid of id
#categoriesToCluster <- na.omit(categoriesToCluster)
str(categoriesToCluster)
summary(categoriesToCluster)
d1 <- replace(categoriesToCluster, is.na(categoriesToCluster), FALSE)
d1 <- d1[0:10000,] # limit due to memory consumption

require(cluster)
#install.packages("ade4")
library(ade4)

## distances
binary.dist.1 <- dist.binary(as.matrix(1 * (d1 > 0)), method=1 )
binary.dist.2 <- dist.binary(as.matrix(1 * (d1 > 0)), method=2 )
binary.dist.3 <- dist.binary(as.matrix(1 * (d1 > 0)), method=3 )
binary.dist.4 <- dist.binary(as.matrix(1 * (d1 > 0)), method=4 )
binary.dist.5 <- dist.binary(as.matrix(1 * (d1 > 0)), method=5 )
binary.dist.6 <- dist.binary(as.matrix(1 * (d1 > 0)), method=6 )
binary.dist.7 <- dist.binary(as.matrix(1 * (d1 > 0)), method=7 )
binary.dist.8 <- dist.binary(as.matrix(1 * (d1 > 0)), method=8 )
binary.dist.9 <- dist.binary(as.matrix(1 * (d1 > 0)), method=9 )
binary.dist.10 <- dist.binary(as.matrix(1 * (d1 > 0)), method=10 )

distance = dist(d1, method = "binary")

## clustering 
hc = hclust(distance)
hc.centroid = hclust(binary.dist1, method="centroid")
hc.ward <- hclust(binary.dist.10, method="ward.D")
plot(hc)
plot(hc.ward)


## groups
group <- cutree(hc.ward, k = 10)
plot(group)
plot(hc.ward, labels=group, xlab="")
data$group <- group # error replacement has 10000 rows, data has 68734
data.limited <- data[0:10000,] 
data.limited$group <- group
head(data.limited)
#cluster.means = aggregate(data,by=list(cutree(hc.simplemathing, k = 10)), mean)


# disconnect from the database
dbDisconnect(con)
