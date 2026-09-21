<div align="center">

# Chennai PG Intelligence

**An end to end machine learning system that scrapes, cleans, models and serves PG rent predictions for Chennai.**

Locality, sharing type and amenities go in. A fair monthly rent, with an honest price band, comes out.

[![Python](https://img.shields.io/badge/Python-3.12+-1a1a1a?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1a1a1a?style=flat-square)](https://xgboost.readthedocs.io/)
[![Optuna](https://img.shields.io/badge/Optuna-1a1a1a?style=flat-square)](https://optuna.org/)
[![MLflow](https://img.shields.io/badge/MLflow-1a1a1a?style=flat-square&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1a1a1a?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1a1a1a?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-1a1a1a?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Azure](https://img.shields.io/badge/Azure_Container_Apps-1a1a1a?style=flat-square&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/container-apps)
[![uv](https://img.shields.io/badge/uv-1a1a1a?style=flat-square)](https://github.com/astral-sh/uv)

### [Open the live app](https://chennai-pg-web.kindrock-91ecbb54.southindia.azurecontainerapps.io/)

`85 commits` · `9 branches` · `1,600+ listings scraped` · `MAE ₹907` · `R² 0.655`

</div>

> **First load takes about two minutes.** Both containers run on an Azure consumption plan that scales to zero when idle, so the first request after a quiet period has to boot the image back up. That is the cold start, not a crash. Wait it out or refresh once and the app comes up.

---

## Contents

- [Why this exists](#why-this-exists)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [How the pipeline works](#how-the-pipeline-works)
- [Branching](#branching)
- [Deployment](#deployment)
- [Model performance](#model-performance)
- [Running it locally](#running-it-locally)
- [API reference](#api-reference)
- [Localities covered](#localities-covered)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Why this exists

A friend and I moved to Chennai to job hunt and spent weeks with no idea what a PG should actually cost. Every listing quotes a number and none of them tell you whether it is fair. Brokers know the going rate for a double sharing room in Velachery. Nobody arriving in the city does.

There is no public dataset for this, so I built one. That constraint shaped the whole project: I reverse engineered NoBroker's internal API, collected the data myself, and spent close to two weeks cleaning it before touching a model. What came out the other end is a full loop rather than a notebook. Scraped data, tracked experiments, a versioned model artifact, two independently containerised services, and a live deployment.

The system returns a predicted rent along with a realistic band derived from the model's held out test error, so it reads as "expect around ₹X, typically ₹Y to ₹Z" instead of a single number pretending to more precision than the data supports.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  COLLECTION                                                                  │
│                                                                              │
│   NoBroker internal API                                                      │
│   /api/v3/multi/property/PG/filter                                           │
│            │                                                                 │
│            │  Scraper/scraper.py  ·  8 geo-mapped areas × MALE / FEMALE       │
│            │  paginate to total_count  ·  randomised 2-4s delays              │
│            ▼                                                                 │
│   Data/raw/chennai_pg_dataset.csv        one row per room type per PG         │
└────────────┬─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PREPROCESSING          src/preprocess.py                                    │
│                                                                              │
│   load_and_clean ──▶ dedupe on (id, occupancy)                                │
│                      drop leaky columns                                       │
│                      rent clipped to ₹1,000-₹15,000                           │
│                      deposit/rent ratio capped at 5x                          │
│                      scores clipped to 0-10                                   │
│         │                                                                     │
│         ▼                                                                     │
│   split 70 / 15 / 15, stratified on occupancy                                 │
│         │                                                                     │
│         ▼                                                                     │
│   target transform:  y = log1p(rent)                                          │
│         │                                                                     │
│         ▼                                                                     │
│   custom transformers                                                         │
│     ├─ BasicFeatureTransformation    log1p(deposit), bools to int8            │
│     └─ LocalMedianImputation         missing scores from the locality's own    │
│                                      median, global median as fallback        │
│         │                                                                     │
│         ▼                                                                     │
│   ColumnTransformer                                                           │
│     ├─ numeric        passthrough                                             │
│     ├─ boolean        passthrough                                             │
│     ├─ occupancy      OrdinalEncoder   SINGLE < DOUBLE < THREE < FOUR         │
│     ├─ gender         OneHotEncoder                                           │
│     ├─ parking        OneHotEncoder                                           │
│     ├─ available_for  OneHotEncoder                                           │
│     └─ locality       TargetEncoder                                           │
└────────────┬─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  TRAINING               src/optuna_tune.py  +  src/train.py                  │
│                                                                              │
│   Optuna, 100 trials, TPE          ──┐                                        │
│     n_estimators, learning_rate,     │  every trial a nested MLflow run       │
│     max_depth, subsample,            ├────────────▶  mlflow.db                │
│     colsample_bytree,                │             params · metrics · best    │
│     reg_alpha, reg_lambda          ──┘                                        │
│     objective: minimise MAE in ₹, not log space                               │
│         │                                                                     │
│         ▼                                                                     │
│   retrain XGBRegressor on train + val (85%) with the best params              │
│         │                                                                     │
│         ▼                                                                     │
│   evaluate once on the untouched 15% test split                               │
│         │                                                                     │
│         ▼                                                                     │
│   models/  full_pipeline.pkl  ·  locality_reference.pkl  ·  metrics.json      │
└────────────┬─────────────────────────────────────────────────────────────────┘
             │
             ├──────────────────────────────┬───────────────────────────────────┐
             ▼                              ▼                                   │
┌──────────────────────────┐   ┌──────────────────────────┐                     │
│  DOCKER IMAGE: api       │   │  DOCKER IMAGE: web       │                     │
│  FastAPI + uvicorn       │   │  Streamlit UI            │                     │
│  pipeline loaded once    │   │  Vice City theme         │                     │
│  at startup (lifespan)   │   │  collects preferences    │                     │
│  GET  /                  │   │                          │                     │
│  GET  /get-localities    │   │                          │                     │
│  POST /prediction        │   │                          │                     │
└────────────┬─────────────┘   └────────────┬─────────────┘                     │
             │                              │                                   │
             ▼                              ▼                                   │
┌──────────────────────────────────────────────────────────────────────────────┐
│  AZURE CONTAINER APPS · South India · consumption plan, scales to zero        │
│                                                                              │
│     ┌────────────────┐           HTTPS            ┌────────────────┐          │
│     │  web app       │ ─────────────────────────▶ │  api app       │          │
│     │  public URL    │                            │  prediction    │          │
│     └────────────────┘                            └────────────────┘          │
│                                                                              │
│  Two containers, not one. Each scales, redeploys and fails on its own.        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Repository layout

```
chennai-pg-price-predictor/
│
├── Scraper/
│   ├── config.py               NoBroker endpoint, headers, base64 geo params per area
│   └── scraper.py              paginated scrape, parse_listing() flattens JSON to rows
│
├── src/
│   ├── configs.py              paths, column groups, model constants, one place
│   ├── preprocess.py           cleaning, splitting, custom transformers, ColumnTransformer
│   ├── optuna_tune.py          Optuna objective wired into MLflow nested runs
│   ├── train.py                tune, retrain, evaluate, persist artifacts
│   └── predict.py              loads the saved pipeline, single record inference
│
├── api/
│   └── main.py                 FastAPI service, health check, localities, prediction
│
├── web/
│   └── app.py                  Streamlit frontend, responsive, calls the API
│
├── models/
│   ├── full_pipeline.pkl       preprocessor and trained XGBRegressor as one sklearn Pipeline
│   ├── locality_reference.pkl  per locality median and mode lookup for backfilling features
│   └── metrics.json            test_mae, test_rmse, test_r2
│
├── Data/raw/                   scraped dataset, gitignored, created at runtime
├── pyproject.toml / uv.lock    dependencies, split into api / web / dev groups
└── .python-version
```

---

## How the pipeline works

### Scraping

`Scraper/scraper.py` hits NoBroker's internal PG filter endpoint for eight pre-mapped Chennai micro markets. The area geo parameters are base64 encoded lat/lon and place IDs, kept in `Scraper/config.py`, and each area is queried for both `MALE` and `FEMALE` listings.

The scraper paginates until the fetched count matches the API's reported `total_count`, with randomised sleeps of two to four seconds between pages and one to two seconds between area and gender switches. `parse_listing()` flattens each property into one row per room type, so a PG offering single, double and triple sharing produces three rows, each with its own rent. Identity, amenities, room, food and house rule fields are pulled out into flat columns.

### Preprocessing

Duplicates are dropped on the `id` and `occupancy` pair. Leaky and low signal columns go. Rent is filtered to a sane ₹1,000 to ₹15,000 band, the deposit to rent ratio is capped at five times, and `transit_score` and `lifestyle_score` are clipped to zero through ten.

The split is 70 / 15 / 15, stratified on occupancy so every sharing type is represented in all three sets. The target is `log1p(rent)`, which means the model trains on log rent and predictions are inverted with `expm1` at inference. Rent distributions are right skewed and this keeps the errors symmetric in the space that matters.

Two custom transformers do the work scikit-learn does not have off the shelf. `BasicFeatureTransformation` applies `log1p` to deposit and casts booleans to `int8`. `LocalMedianImputation` fills missing transit and lifestyle scores with the median for that specific locality rather than a global median, because a missing transit score in Sholinganallur means something different from one in Guindy. The global median is the fallback when a locality has nothing to impute from.

Both fit only on the training split, so the imputation medians never see validation or test data.

### Tuning and training

Optuna runs a hundred trial Bayesian search over `n_estimators`, `learning_rate`, `max_depth`, `subsample`, `colsample_bytree`, `reg_alpha` and `reg_lambda`. The objective minimises MAE in rupees on the validation set after inverse transforming, not MAE in log space, because an optimiser told to minimise log error will happily trade away accuracy on expensive listings.

Every trial is logged as a nested MLflow run, with the best parameters and best MAE on the parent run. The final model is retrained on train and validation combined, eighty five percent of the data, then evaluated exactly once against the untouched test split.

`save_artifacts()` writes the full pipeline, the locality reference table, and the metrics file.

### Serving

`api/main.py` loads the pipeline once at startup through a lifespan handler rather than per request. It takes the handful of high level inputs a user can reasonably supply and expands them into the full feature vector the model expects, backfilling latitude, longitude, deposit and unspecified amenities from the locality reference table. Predicted rent is rounded to the nearest ₹500 and returned with a band of plus or minus the test MAE.

`web/app.py` is a Streamlit frontend with a GTA Vice City themed CSS and SVG layer, responsive down to phone widths, that posts preferences to the API and renders the result.

---

## Branching

`main` stays stable and deployable. Every piece of work happens on its own branch and merges through a pull request once it runs, which is where most of the 85 commits live.

| Branch | Purpose |
|---|---|
| `main` | Stable, deployable, only updated through PR merges |
| `feature/EDA` | Exploratory analysis on the scraped dataset |
| `preprocessing` | Cleaning, feature engineering, the custom transformers |
| `modeling` | XGBoost iteration and evaluation |
| `prod-pipeline` | The notebook to script refactor, exploratory work turned into production modules |
| `backend` | FastAPI service, merged via PR #4 |
| `frontend/streamlit` | Streamlit UI and the Vice City theme, merged via PR #5 |
| `deploy/docker-azure` | Dockerfiles and Azure Container Apps deployment |
| `dev` | Integration branch ahead of `main` |

---

## Deployment

| Component | Where it runs | Notes |
|---|---|---|
| `api` container | Azure Container Apps, South India | FastAPI and the trained pipeline, loaded once at startup |
| `web` container | Azure Container Apps, South India | Streamlit UI, talks to the API over HTTPS |
| Scaling | Consumption plan, scales to zero | Cheap when idle, roughly two minute cold start on the first hit |
| Build source | `deploy/docker-azure` | Dockerfiles and deployment config, PR merged into `main` |

The API and the frontend are two separate images on purpose. It mirrors how this would actually be run: a stateless prediction service that any client could call, and a disposable UI that can be redeployed without touching the model. It also means the API can be tested directly without starting the frontend.

---

## Model performance

Evaluated on the held out test split, in rupees, inverse transformed from log space.

| Metric | Value | Reading |
|---|---|---|
| MAE | ₹907.11 | Typical prediction is off by about ₹900 |
| RMSE | ₹1,375.81 | Larger misses weighted more heavily |
| R² | 0.655 | Explains roughly 65% of rent variance |

An R² of 0.655 is the honest ceiling for this feature set. Rent in Chennai depends on things the listing never states, such as the actual state of the building, how far the walk to the bus stop really is, and what the owner thinks they can get. The band the API returns is there because of exactly that.

XGBoost was picked after benchmarking against linear regression and other tree ensembles, not by default.

---

## Running it locally

**Requires** Python 3.12 or newer and [`uv`](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/DineshMSDian/chennai-pg-price-predictor.git
cd chennai-pg-price-predictor
uv sync
```

Scrape fresh data, optional, needs a `USER_ID` in a `.env`:

```bash
cd Scraper
uv run scraper.py
```

Train. `train.py` expects an MLflow server on port 5000:

```bash
uv run mlflow ui --port 5000 &
uv run -m src.train
```

That runs the search, retrains, evaluates and writes `models/full_pipeline.pkl`, `models/locality_reference.pkl` and `models/metrics.json`.

Serve:

```bash
uv run fastapi run api/main.py                  # API on :8000
API_URL=http://localhost:8000 uv run streamlit run web/app.py
```

---

## API reference

Base URL `http://localhost:8000`.

**`GET /`** health check.

```json
{ "status": "As you can see im not dead!?" }
```

**`GET /get-localities`** every locality the model was trained on, used to populate the dropdown.

```json
{ "localities": ["Adambakkam", "Alandur", "..."] }
```

**`POST /prediction`**

<details>
<summary>Request</summary>

```json
{
  "locality": "Velachery",
  "gender": "MALE",
  "occupancy": "Double",
  "available_for": "Student",
  "food_included": true,
  "wifi": true,
  "laundry": false,
  "room_ac": false,
  "parking": "Bike"
}
```
</details>

<details>
<summary>Response</summary>

```json
{
  "predicted_rent": 8500.0,
  "lower": 7592.89,
  "upper": 9407.11,
  "locality": "Velachery",
  "occupancy": "Double"
}
```
</details>

---

## Localities covered

Eight geo-mapped micro markets, chosen because they are where people actually look for a PG when they move to Chennai for work or college.

| Region | Localities |
|---|---|
| South Chennai | Perungalathur, Old and New Perungalathur, Vandalur |
| Suburban south | East Tambaram, Tambaram West, GST Road Tambaram |
| IT corridor, OMR | Sholinganallur, OMR Karapakkam |
| IT corridor, ECR | Tharamani, Maraimalai Nagar, ECR Thiruvanmiyur |
| Central south | Velachery, Adambakkam, IIT Madras |
| Coastal | Thiruvanmiyur, Kamaraj Nagar, Kottivakkam |
| Central | Guindy, Saidapet, Alandur |
| West central | Vadapalani, Ashok Nagar, Kodambakkam |

---

## Roadmap

- [x] Separate Docker images for API and web
- [x] Deploy to Azure Container Apps
- [x] Responsive frontend, mobile and desktop
- [ ] GitHub Actions to build and push containers on merge to `main`
- [ ] Warm-up ping or a minimum replica to kill the cold start
- [ ] Model versioning through the MLflow Model Registry
- [ ] More localities: further south on OMR, Porur, Perambur
- [ ] Real transit and lifestyle scores from an API instead of local median imputation
- [ ] Quantile regression for the prediction band instead of a static MAE offset

---

## Author

**Dinesh T** · AI and ML engineer, Chennai

[GitHub](https://github.com/DineshMSDian) · [LinkedIn](https://linkedin.com/in/dinesht7013) · [Email](mailto:dinesh2742004@gmail.com) · [Live app](https://chennai-pg-web.kindrock-91ecbb54.southindia.azurecontainerapps.io/)

<sub>The UI theme is a nod to GTA Vice City. Grand Theft Auto: Vice City © Rockstar Games.</sub>