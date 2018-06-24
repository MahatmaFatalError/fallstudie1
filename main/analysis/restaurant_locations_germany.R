
library('RPostgreSQL')

# multithreading
library(parallel)
mcaffinity()
ncore = detectCores()
f<-function(x)system("dd if=/dev/urandom bs=32k count=2000 | bzip2 -9 >> /dev/null", ignore.stdout=TRUE,ignore.stderr=TRUE,wait=FALSE)
#syscall = system("blastp -query query.fasta -db db.fasta -num_threads 16 -outfmt \"6 qseqid sseqid pident ppos evalue bitscore qcovs\" -out out.tsv")
#mclapply(1:ncore,syscall,mc.cores=ncore)
mclapply(1:ncore,f,mc.cores=ncore)

## connect to db
pg = dbDriver("PostgreSQL")
con = dbConnect(pg, user="postgres", password="team123",
                host="35.190.205.207", port=5432, dbname="fonethd")

## create view restaurants_in_germany as (
##  select r.name, r.rating, r.price_range, r.review_count , r.city, r.state, c.name as category, city.population_sqkm, city.buying_power , city.rent_avg  from restaurant r inner join food_category c on r.id = c.restaurant_id
## inner join city on r.city = city.name
##  where city is not null and is_closed = false)

## dtab = dbReadTable(con, "restaurant")
dtab = dbGetQuery(con, "select * from restaurants_in_germany")
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

cityCat = factor(dtab$city)
#dtab$city = cityCat
stateCat = factor(dtab$state)
dtab$state = stateCat

## linear Regression
fit.lr <- lm(rating ~ ., data=dtab ) #+ price_range
summary(fit.lr)

## tree
library(partykit)
fit.t <- ctree(rating ~ price_range + city + review_count + category, data=dtab)
plot(fit.t)


library(effects)
plot(effect("price_range", fit.lr))


# disconnect from the database
dbDisconnect(con)
