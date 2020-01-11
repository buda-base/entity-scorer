# BUDA Entity Scorer

This is a simple Python script to create entity scores for entities. It walks the work, person and place repositories, which must be cloned locally.

See [this Google Doc](https://docs.google.com/document/d/10ujEnE5YH6CmBIPpTHeLqJE6F45uppUVTFhskBzUPvE/edit?usp=sharing) for more about the idea.

## Test

Searching for sgam po pa results in 16 results (P898, P5575, P1844, P2577, P354, P834, P958, P1854, P1857, P5809, P2GS984), but we expect that P1844 will have the highest score.

## Use

Change the `GITDIRS` variable, run

```sh
python3 entity-score.py
```

then upload with:

```sh
curl -X PUT -H Content-Type:text/turtle -T entityScores.ttl -G http://buda1.bdrc.io:13180/fuseki/corerw/data --data-urlencode 'graph=http://purl.bdrc.io/graph/entityScores'
```