
library(plumber)
pr <- plumb("save_content_api.R")
pr$run(port = 8000, host = "0.0.0.0")
