-- occurrences
select count(*) from artifacts;

-- distinct_contents
select count(distinct file_sha) from artifacts;

-- representatives
select count(*) from artifacts where dedup_primary=1;

-- repositories
select count(*) from repos;

-- siblings
select count(*) from artifact_siblings;

-- history_flags
select history_fetched, count(*) from artifacts group by history_fetched;

-- history_with_multiple_commits
select count(*) from artifacts where history_fetched=1 and commit_count>1;

-- location_classes
select location_class,count(*) from artifacts group by location_class;

-- example
select repo_full_name,path,name,description,first_commit_at,last_commit_at,commit_count,substr(content,1,1700) from artifacts where dedup_primary=1 and history_fetched=1 and commit_count>2 and frontmatter_valid=1 order by file_sha limit 1;
