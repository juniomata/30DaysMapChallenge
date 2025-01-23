# Load required libraries
library(shiny)
library(arrow)
library(sf)
library(dplyr)
library(tigris)
library(rdeck)
library(rgeoboundaries)
library(viridisLite)
library(wk)

# Set Mapbox token and other options
options(tigris_use_cache = TRUE)
options(rdeck.mapbox_access_token = "pk.eyJ1IjoiZ29kZnJpZWRqOTgiLCJhIjoiY2s4YnZvcHBuMGQ2MjNmcGtmZnhpc29zbiJ9.XGuwlmN-I1MFnS5Yhqdxqw")

# Function to load Jakarta boundary and filter building data
load_data <- function() {
  # Retrieve Indonesia's administrative level 1 boundaries
  indo_adm1 <- gb_adm1("Indonesia")
  
  # Filter to obtain Jakarta's boundary
  jakarta_boundary <- indo_adm1 %>%
    filter(shapeName == "Jakarta Special Capital Region")
  
  # Set CRS
  jakarta_boundary <- st_transform(jakarta_boundary, crs = 4326)
  
  # Extract Jakarta's bounding box
  jakarta_bbox <- st_bbox(jakarta_boundary)
  
  # Pull Overture building data (bounding box filtering)
  buildings <- open_dataset('s3://overturemaps-us-west-2/release/2024-05-16-beta.0/theme=buildings?region=us-west-2')
  
  # Filter data
  jakarta_buildings_bbox <- buildings %>%
    filter(bbox$xmin > jakarta_bbox["xmin"],
           bbox$ymin > jakarta_bbox["ymin"],
           bbox$xmax < jakarta_bbox["xmax"],
           bbox$ymax < jakarta_bbox["ymax"]) %>%
    select(id, geometry, height) %>%
    collect() %>%
    st_as_sf(crs = 4326) %>%
    mutate(height = ifelse(is.na(height), 8, height))
  
  # Collect dataset into a local data frame
  jakarta_buildings_df <- collect(jakarta_buildings_bbox)
  
  # Convert buildings data frame to an sf object
  jakarta_buildings_sf <- st_as_sf(jakarta_buildings_df, wkt = "geometry", crs = 4326)
  
  # Perform the spatial intersection to clip buildings within Jakarta
  jakarta_buildings <- st_intersection(jakarta_buildings_sf, jakarta_boundary)
  
  # Handle missing height values (optional)
  jakarta_buildings <- jakarta_buildings %>%
    mutate(height = ifelse(is.na(height), 8, height))
  
  return(jakarta_buildings)
}

# Load data once at app start
jakarta_buildings <- load_data()

# Define UI
ui <- fillPage(
  titlePanel("Jakarta 3D Buildings Visualization"),
  rdeckOutput("map", height = "100vh")  # 100vh ensures full viewport height
)

# Define server logic
server <- function(input, output, session) {
  
  output$map <- renderRdeck({
    rdeck(
      map_style = mapbox_light(),  # Using Mapbox Light basemap
      initial_view_state = view_state(
        center = c(106.8456, -6.2088), # Jakarta coordinates
        zoom = 11.3,
        pitch = 50
      )
    ) |> 
      add_polygon_layer(
        data = jakarta_buildings,
        name = "Jakarta Buildings",
        get_polygon = geometry,
        get_elevation = height,
        get_fill_color = scale_color_linear(
          col = height,
          palette = viridisLite::inferno(100, direction = -1)
        ),
        extruded = TRUE,
        opacity = 0.5
      )
  })
  
  # Download GeoJSON file
  output$download_geojson <- downloadHandler(
    filename = function() { "jakarta_buildings.geojson" },
    content = function(file) {
      file.copy("jakarta_buildings.geojson", file)
    }
  )
}

# Run the application
shinyApp(ui, server)
