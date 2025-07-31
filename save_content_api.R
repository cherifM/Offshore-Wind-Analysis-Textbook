
# save_content_api.R
# Plumber API for content editing

library(plumber)
library(jsonlite)

# Configuration
CONTENT_DIR <- "content"
BACKUP_DIR <- "content_backups"

#* @apiTitle Offshore Wind Textbook Content Editor API
#* @apiDescription API for saving and managing textbook content

#* Save content for a specific page
#* @param page The page identifier (e.g., "theory", "measurement")
#* @param content The markdown content
#* @param author The author making the change (optional)
#* @post /save
function(req, page = "", content = "", author = "anonymous") {
    # Validate inputs
    if (page == "" || content == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page and content are required"
        ))
    }
    
    # Sanitize page name
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    
    # Create backup
    timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
    backup_dir <- file.path(BACKUP_DIR, page)
    dir.create(backup_dir, recursive = TRUE, showWarnings = FALSE)
    
    current_file <- file.path(CONTENT_DIR, paste0(page, ".md"))
    if (file.exists(current_file)) {
        backup_file <- file.path(backup_dir, paste0(page, "_", timestamp, ".md"))
        file.copy(current_file, backup_file)
    }
    
    # Save new content
    tryCatch({
        writeLines(content, current_file)
        
        # Log the change
        log_entry <- list(
            page = page,
            timestamp = Sys.time(),
            author = author,
            size = nchar(content)
        )
        
        log_file <- "content_changes.log"
        write(toJSON(log_entry, auto_unbox = TRUE), 
              file = log_file, append = TRUE)
        
        # Trigger rebuild
        system("python3 build.py", intern = FALSE, wait = FALSE)
        
        return(list(
            success = TRUE,
            message = "Content saved successfully",
            backup = basename(backup_file)
        ))
    }, error = function(e) {
        res$status <- 500
        return(list(
            success = FALSE,
            message = paste("Error saving content:", e$message)
        ))
    })
}

#* Get content for a specific page
#* @param page The page identifier
#* @get /content
function(page = "") {
    if (page == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page parameter is required"
        ))
    }
    
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    file_path <- file.path(CONTENT_DIR, paste0(page, ".md"))
    
    if (!file.exists(file_path)) {
        res$status <- 404
        return(list(
            success = FALSE,
            message = "Page not found"
        ))
    }
    
    content <- paste(readLines(file_path), collapse = "
")
    
    return(list(
        success = TRUE,
        content = content,
        page = page
    ))
}

#* List available pages
#* @get /pages
function() {
    files <- list.files(CONTENT_DIR, pattern = "\.md$", full.names = FALSE)
    pages <- gsub("\.md$", "", files)
    
    page_info <- lapply(pages, function(p) {
        file_path <- file.path(CONTENT_DIR, paste0(p, ".md"))
        list(
            id = p,
            name = gsub("-", " ", p),
            modified = file.info(file_path)$mtime,
            size = file.info(file_path)$size
        )
    })
    
    return(list(
        success = TRUE,
        pages = page_info
    ))
}

#* Get backup history for a page
#* @param page The page identifier
#* @get /backups
function(page = "") {
    if (page == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page parameter is required"
        ))
    }
    
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    backup_dir <- file.path(BACKUP_DIR, page)
    
    if (!dir.exists(backup_dir)) {
        return(list(
            success = TRUE,
            backups = list()
        ))
    }
    
    backup_files <- list.files(backup_dir, full.names = TRUE)
    backups <- lapply(backup_files, function(f) {
        list(
            filename = basename(f),
            timestamp = file.info(f)$mtime,
            size = file.info(f)$size
        )
    })
    
    return(list(
        success = TRUE,
        backups = backups
    ))
}
