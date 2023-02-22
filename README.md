# philly-democratic-voting-clusters
This repo contains the data behind the analysis of Philadelphia Democratic voting patterns that [the Philadelphia Inquirer published on February 21, 2023](https://www.inquirer.com/politics/election/inq2/philadelphia-democrats-race-class-voting-data-20230221.html).

This expands upon the methodology we provided in the "About the analysis" section of the article.

## Background and results
Philadelphia has a mayoral primary coming up on May 16, and in the words of our veteran politics reporter Julia Terruso, the Democratic primary amounts to a coronation of the next mayor in this very blue city. But we know that Philly Dems aren't monolithic, and we wanted to be analytical about understanding what voting "blocs" might exist in Democratic party politics. That, after all, is the lens in which mayoral candidates will have to think about their constituencies.

To do that, we assembled eight years of Democratic primary data at the precinct level, for elections big and small from 2015 through 2022. We fed those results into a [k-means clustering algorithm](https://en.wikipedia.org/wiki/K-means_clustering) to group precincts. We tried different sets of elections and different numbers of clusters to find something interpretively meaningful and explanatorily satisfying.

Six was the number of clusters that seemed to explain the variation the best, while still mapping to easily understandable groups in the city. It's worth noting that three-, four-, and five-cluster maps yielded similar results, and sussed out race and class boundaries in similar ways.

## Where the data came from
We used three sources:
* Primary election results from 2015 through 2022 came from the [Philadelphia city commissioners](https://vote.phila.gov/resources-data/past-election-results/).
* Most demographic data came from the Census Bureau's American Community Survey (ACS). We used the 2017-2021 vintage five-year ACS data.
* The number, location, and age of registered Democrats were derived from the Jan. 30, 2023 edition of the voter rolls from the Pennsylvania Department of State.

## How we handled race and ethnicity
The analysis grouped residents into one of five mutually exclusive racial and ethnic categories, which is an oversimplification that doesn’t always match how people identify. Anyone who is listed as Hispanic or Latino is counted in that group, regardless of race; all other categories group non-Hispanic residents by race. Therefore, in this analysis:
* "Hispanic or Latino" residents can be of any race(s)
* "White" residents are non-Hispanic white residents of no other race
* "Black" residents are non-Hispanic Black residents of no other race
* "Asian American and Pacific Islander" residents are non-Hispanic residents of either of those races and no other
* All "other and multiracial" residents are those from other racial and ethnic groups, such as Native Americans, or of multiple races.

## How we put the data together
There were two main difficulties in putting this data together:
1. Precinct boundaries change from time to time, so election results aren't directly comparable from year to year.
2. Other than race and ethnicity data, which was collected in the 2020 Census and is available at the precinct level, other demographics (like education, income, etc.) are collected by the Census Bureau in the ACS. There, the smallest level of resolution available is the census tract. Tracts are much larger geographies than precincts.

The solution in both cases was to "crosswalk" data to match contemporary precinct boundaries using a technique called "population weighting." We determined which census blocks lay within each larger boundary. If the geographic center of that block was within one precinct or tract, we attributed it to that unit. We then weighted tract demographics and past precinct results by how much of their population lay within each current precinct.

If that sounds confusing or complicated, that's because it is. See Jonathan Tannen's [excellent write-up and tutorial](https://sixtysixwards.com/home/crosswalk-tutorial/).

Finally, individual voter roll records were aggregated at the precinct level to determine the number of active Democrats falling within each precinct boundary and to calculate their average age (precincts are available directly in the rolls).

## How we normalized the data and performed the analysis
Having "crosswalked" eight years of primary data to conform to the most recent set of precinct boundaries, we had to prepare it for use in the algorithm. One thing to bear in mind for clustering is that the data should be "normalized:" each variable should have the same range of possible values.

For election results, that range is 0-1, with each value denoting the share of the vote that a particular candidate earned in their respective race.

One special case was with multi-candidate elections, as with judicial elections or at-large City Council races, in which voters choose multiple candidates. In those cases, we normalized the results to sum up not to 1, but to the number of votes that an individual voter could cast for that office. For example, if voters could choose up to five candidates from a list for one office, each candidate's share of the vote was calculated on a 0-5 scale.

The result was a dataset which included one row per contemporary precinct (for a total of 1703), and one column for every candidate who competed in a primary between 2015 and 2022.

Note that uncompetitive races were mostly excluded. For example, the 2022 gubernatorial primary was uncontested, so we left it out. The 2020 presidential primary was contested on paper, but Joe Biden had already clinched the nomination by the time of Pennsylvania's primary, so we left that one out too.

Once the data was ready, we fed it iteratively into a set of k-means algorithms, testing various clusters for distortion using the ["elbow method"](https://en.wikipedia.org/wiki/Elbow_method_(clustering)). That suggested we should focus on k in the three to six cluster range.

## Notes on the data as published
Each row of the data represents one precinct.
* The column `prec_20` is the unique precinct identifier. It concatenates the city ward and division numbers.
* There are 122 columns of election results, structured as described above. The column names are of the format "OFFICE_CANDIDATENAME." The first of these is `COUNCIL AT LARGE-DEM_ALLAN DOMB` and the last is `LIEUTENANT GOVERNOR DEM - Write-in`.
* Cluster ID values for each of three-, four-, five-, and six-cluster groupings (`clust_3`,`clust_4`,`clust_5`, and `clust_6`). These are  automatically generated numeric IDs, and they aren't consistent from grouping to grouping.
* Precinct-level racial demographic data directly from the 2020 Census, in the columns `hisp`, `black`, `white`, `aapi`, and `other`. Shares of the total population are given as `hisp_share`, `black_share`, `white_share`, `aapi_share`, and `other_share`. This considers the adult (18+) population only (table P4 in the Census).
* Raw precinct-level ACS demographics crosswalked on a population-weighted basis from census-tract-level data. These are the 6-digit fields that start with the letter "B." A dictionary denoting the value of these is [available from the Census Bureau](https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html).
* Calculated ACS demographics:
    * `median_age` is the median age of all residents
    * `mean_household` is the average number of residents per household
    * `foreign_share` is the share of residents born outside the USA (USA includes Puerto Rico and other territories)
    * `noneng_share` is the share of residents speaking a language other than English at home, irrespective of how well they speak English
    * `edu_attain` is the share of residents having earned a Bachelor's degree or higher
    * `mean_household_inc` is the average income of households
    * `pov` is the poverty rate of individuals
    * `mean_commute` is the average commute time for workers
    * `two_parent` is the share of households with children that have two parents living at home
    * `child_house` is the share of households where any number of children under 18 are resident
    * `vet_share` is the share of adults who are veterans of the US military
    * `vacancy` is the share of housing units in the precinct that are unoccupied
    * `renter_rate` is the share of households who rent rather than own their homes

## Acknowledgements and other work
We are indebted to a handful of people outside The Inquirer for their help in thinking through this analysis. Most especially, we'd like to thank Dan Hopkins at the University of Pennsylvania for his methodological feedback.

Others have similarly clustered Philly's electorate; see e.g. Tannen's [four-cluster schema](https://sixtysixwards.com/home/philadelphias-changing-voting-blocs/).

## Contact
Please email Aseem Shukla at ashukla@inquirer.com with any questions or comments.