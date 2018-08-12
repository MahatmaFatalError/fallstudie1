
library('RPostgreSQL')

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

##### hclust for binary matrix

data = dbGetQuery(con, "select * from restaurants_categories_flatter") # 68.734 rows
summary(data)

categoriesToCluster <- data[,-1]   # delete id
#categoriesToCluster <- na.omit(categoriesToCluster)
str(categoriesToCluster)
summary(categoriesToCluster)

require(cluster)
#install.packages("ade4")
library(ade4)

# dist <- dist.binary(categoriesToCluster )

d1 <- replace(categoriesToCluster, is.na(categoriesToCluster), FALSE)

distance = dist(d1[0:10000,], method = "binary")

hc = hclust(distance)
plot(hc)

group <- cutree(hc, k = 10)
str(group)
plot(hc, labels=group, xlab="")

cluster.means = aggregate(data,by=list(cutree(hc, k = 6)), mean)


# disconnect from the database
dbDisconnect(con)
