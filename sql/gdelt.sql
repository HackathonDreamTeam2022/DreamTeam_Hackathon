WITH ngram_counts AS
    (
    SELECT url AS article_url, date AS article_date, REGEXP_REPLACE(LOWER(CONCAT(ngram, " ", REGEXP_EXTRACT(post, r'([^\s]+)'))), r'[\.\",*:()\[\]/|\n@]', '') AS phrase
    FROM `gdelt-bq.gdeltv2.webngrams`
    WHERE DATE(date) = "2022-04-07" AND LANG = "en"
    UNION ALL
    SELECT url, date, REGEXP_REPLACE(LOWER(ngram), r'[\.\",*:()\[\]/|\n@]', '') AS phrase
    FROM `gdelt-bq.gdeltv2.webngrams`
    WHERE DATE(date) = "2022-04-07" AND LANG = "en"
    )
SELECT t1.article_url, t1.article_date, article_title, mid, gdelt_entity_name, relevant_mentions/total_words AS corpus_score, sentiment_magnitude, sentiment_score, sentiment_salience
FROM
    (
    SELECT article_url, article_date, COUNT(*) AS relevant_mentions
    FROM ngram_counts
    -- WHERE phrase IN (SELECT * FROM `hackathon-team-10.corpus.corpus`)
    GROUP BY article_url, article_date
    ) AS t1
-- Inner join with NGRAMS to get word count
INNER JOIN
    (
    SELECT article_url, article_date, COUNT(*) AS total_words
    FROM ngram_counts
    GROUP BY article_url, article_date
    ) AS t2
ON (DATE(t1.article_date) = DATE(t2.article_date)) AND (t1.article_url = t2.article_url)
-- Inner join with GDELT entities to get entity and sentiment
INNER JOIN
    (
    SELECT url, date, mid, name AS gdelt_entity_name, magnitude AS sentiment_magnitude, score AS sentiment_score, avgSalience AS sentiment_salience
    FROM `gdelt-bq.gdeltv2.geg_gcnlapi`, UNNEST(entities)
    -- WHERE LANG = "en" AND DATE(date) = "2022-04-07" AND mid IN (SELECT mid FROM `hackathon-team-10.companies.companies_list`)
    WHERE LANG = "en" AND DATE(date) = "2022-04-07"
    ) AS t3
ON (DATE(t1.article_date) = DATE(t3.date)) AND (t1.article_url = t3.url)
-- Inner join with GDELT articles to get title
INNER JOIN
    (
    SELECT url, date, title AS article_title
    FROM `gdelt-bq.gdeltv2.gal`
    WHERE LANG = "en" AND DATE(date) = "2022-04-07"
    ) AS t4
ON (DATE(t1.article_date) = DATE(t4.date)) AND (t1.article_url = t4.url)
ORDER BY t1.article_date DESC
LIMIT 10000




SELECT DISTINCT(date)
FROM FROM `gdelt-bq.gdeltv2.webngrams`
WHERE LANG = "en" AND DATE(date) = "2022-04-07"
