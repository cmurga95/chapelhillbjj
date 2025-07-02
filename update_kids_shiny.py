from shiny import App, reactive, render, ui
import pandas as pd
import requests
from datetime import datetime
from shiny.types import SilentException
import supabase_endpoint


# === CONFIG ===
API_BASE = "https://kids-api-access.onrender.com"

# === HELPERS ===
def load_kids():
    """Load kids table via FastAPI"""
    try:
        data = supabase_endpoint.get_checkins_kids()
        # response.raise_for_status()
        # data = response.json()
        df = pd.DataFrame(data)
        df["last_promotion_date"] = pd.to_datetime(df["last_promotion_date"], errors="coerce")
        return df
    except Exception as e:
        print(f"Error loading kids: {str(e)}")
        return pd.DataFrame(columns=["client", "last_promotion_date", "class"])

def load_kids_view():
    """Load kids VIEW via FastAPI"""
    try:
        # response = requests.get(f"{API_BASE}/checkins_kids_view")
        # response.raise_for_status()
        data = supabase_endpoint.get_checkins_kids_view()
        df = pd.DataFrame(data)
        df["last_promotion_date"] = pd.to_datetime(df["last_promotion_date"], errors="coerce")
        return df
    except Exception as e:
        print(f"Error loading kids: {str(e)}")
        return pd.DataFrame(columns=["client", "last_promotion_date", "current_rank", "attendance_since_promotion"])

def merged_data():
    """Merge kids data with kids view"""
    kids_df = load_kids()
    kids_view_df = load_kids_view()
    
    if kids_df.empty or kids_view_df.empty:
        return pd.DataFrame(columns=["client", "last_promotion_date", "current_rank", "attendance_since_promotion", "class"])
    
    merged_df = pd.merge(
        kids_df[['client', 'start_date', 'first_name', 'last_name', 'current_rank',
       'stripes', 'class']], 
        kids_view_df[['client','attendance_since_promotion', 'last_promotion_date']], 
        on="client", 
        how="inner"
    )
    
    return merged_df[['first_name', 'last_name', 'attendance_since_promotion',
                      'last_promotion_date', 'current_rank', 'stripes', 'class', 'start_date', 'client']]

# === UI ===
app_ui = ui.page_fluid(
    ui.h2("Kids Promotion Dates"),
    # ui.input_date("date1", "Has default date:", value="2016-02-29"),
    # ui.layout_columns(
    ui.card(
        ui.card_header("Youth Jiu Jitsu (Ages 4-8)"),
        ui.output_data_frame("kids_table_4_8"),
        style="height: 600px; overflow-y: auto;"
        ),
    ui.card(
        ui.card_header("Youth Jiu Jitsu (Ages 8-14)"),
        ui.output_data_frame("kids_table_8_14"),
        style="height: 600px; overflow-y: auto;"
    # ),
    #     col_widths=[6, 6]
    ),
    ui.input_action_button("save", "Save Changes", class_="btn-primary"),
    # ui.output_text("status")
)

# === SERVER ===
def server(input, output, session):
    kids_df = reactive.value(merged_data())
    sort_column = reactive.value("client")
    sort_ascending = reactive.value(True)
    secondary_sort_column = reactive.value(None)
    secondary_sort_ascending = reactive.value(True)

    @reactive.Effect
    def update_sorting():
        if "sort_column" in input:
            if input.sort_column() == sort_column():
                sort_ascending.set(not sort_ascending())
            else:
                if sort_column() is not None:
                    secondary_sort_column.set(sort_column())
                    secondary_sort_ascending.set(sort_ascending())
                sort_column.set(input.sort_column())
                sort_ascending.set(True)

    # @reactive.Effect
    # def edit_date_input():
    #     if 

    @reactive.Calc
    def sorted_data():
        df = kids_df().copy()
        if df.empty:
            return df
        
        primary_col = sort_column()
        primary_asc = sort_ascending()
        secondary_col = secondary_sort_column()
        secondary_asc = secondary_sort_ascending()
        
        sort_cols = []
        sort_orders = []
        
        if primary_col:
            sort_cols.append(primary_col)
            sort_orders.append(primary_asc)
        
        if secondary_col:
            sort_cols.append(secondary_col)
            sort_orders.append(secondary_asc)
        
        if "attendance_since_promotion" in sort_cols:
            df = df.copy()
            df["attendance_since_promotion"] = df["attendance_since_promotion"].fillna(0)
        
        try:
            return df.sort_values(
                by=sort_cols,
                ascending=sort_orders,
                na_position='first'
            )
        except Exception as e:
            print(f"Sorting error: {str(e)}")
            return df

    def create_kids_df(class_name):
        df = sorted_data()
        filtered_df = df[df["class"] == class_name].copy()
        
        # Format dates for display
        filtered_df["last_promotion_date"] = pd.to_datetime(filtered_df["last_promotion_date"]).dt.strftime('%Y-%m-%d')
        
        return filtered_df

    @output
    @render.data_frame
    def kids_table_4_8():
        df = create_kids_df('Youth Jiu Jitsu (Ages 4-8)')
        return render.DataGrid(
            df,
            editable=["last_promotion_date", 
                      "stripes", 
                      "current_rank"],
            selection_mode="none",
            filters=True
        )
    
    # Handle type conversion for edits
    @kids_table_4_8.set_patch_fn
    def _(*, patch: render.CellPatch) -> render.CellValue:
        col_name = create_kids_df('Youth Jiu Jitsu (Ages 4-8)').columns[patch["column_index"]]
        
        if col_name == "last_promotion_date":
            return str(patch["value"])  # Ensure date stays as string
        elif col_name == "stripes":
            return int(patch["value"])
        elif col_name == "current_rank":
            return str(patch["value"])
        return patch["value"]
    
    # Main editable table for 8-14 age group
    @render.data_frame
    def kids_table_8_14():
        df = create_kids_df('Youth Jiu Jitsu (Ages 8-14)')
        return render.DataGrid(
            df,
            editable=["last_promotion_date", 
                      "stripes", 
                      "current_rank"],

            # {
            #     "last_promotion_date": True,
            #     "stripes": True, 
            #     "current_rank": True,
            #     # "start_date": False,
            #     # "client": False, 
            #     # "first_name": False,
            #     # "last_name": False
            # },
            selection_mode="none",
            filters=True
        )
    
    # Handle type conversion for edits
    @kids_table_8_14.set_patch_fn
    def _(*, patch: render.CellPatch) -> render.CellValue:
        col_name = create_kids_df('Youth Jiu Jitsu (Ages 8-14)').columns[patch["column_index"]]
        
        if col_name == "last_promotion_date":
            return str(patch["value"])
        elif col_name == "stripes":
            return int(patch["value"])
        elif col_name == "current_rank":
            return str(patch["value"])
        return patch["value"]

    # Save handler using proper renderer methods
    @reactive.Effect
    @reactive.event(input.save)
    def _():
        updates = []
        
        # Process edits from both tables
        for renderer, class_name in [
            (kids_table_4_8, 'Youth Jiu Jitsu (Ages 4-8)'),
            (kids_table_8_14, 'Youth Jiu Jitsu (Ages 8-14)')
        ]:
            # Get all patches (edits) for this table
            patches = renderer.cell_patches()
            
            if not patches:
                continue
                
            # Get the original data to map row indices to clients
            original_df = create_kids_df(class_name)
            # print(patches)
            for patch in patches:
                col_name = original_df.columns[patch["column_index"]]
                if col_name not in ["last_promotion_date", "stripes", "current_rank"]:
                    ui.notification_show(f"Cannot edit {col_name} - this field is read-only", 
                            type="warning", 
                            duration=2)
                if col_name in ["last_promotion_date", "stripes", "current_rank"]:
                    client = original_df.iloc[patch["row_index"]]["client"]
                    updates.append({
                        "client": client,
                        "field": col_name,
                        "value": patch["value"]
                    })
                    #needed for filter payload
                    
                #payload
                # stripes = original_df.iloc[patch["row_index"]]["stripes"]
                # start_date = original_df.iloc[patch["row_index"]]["start_date"]
                # current_rank = original_df.iloc[patch["row_index"]]["current_rank"]

            print(updates)
        # Send updates to API
        success_count = 0
        # Good pattern: map fields to functions (not results!)
        endpoint_map = {
            "last_promotion_date": supabase_endpoint.update_promotion_date,
            "stripes": supabase_endpoint.update_promotion_stripes,
            "current_rank": supabase_endpoint.update_promotion_rank,
            "start_date": supabase_endpoint.update_start_date
        }

        for update in updates:
            d = {"client": update["client"], "field": update["field"], "value": update["value"]}
            try:
                fn = endpoint_map.get(update["field"])
                if fn is None:
                    print(f"Unknown field: {update['field']}")
                    continue  # Skip if no matching update function

                result = fn(d)  # ← Now only ONE function runs!
                # print(f"Update result: {result}")
                print(f"Updated {update['field']} for client {update['client']}: {result}")
                if result.get("status") == "success":
                    success_count += 1
                else:
                    print(f"Failed to update {update['field']} for client {update['client']}: {result}")
            except Exception as e:
                print(f"Error updating {update['field']} for client {update['client']}: {e}")
        
        # Refresh data if updates were successful
        if success_count > 0:
            kids_df.set(merged_data())
            ui.notification_show(f"Updated {success_count} records!", duration=3)
        elif updates:  # Had updates but none succeeded
            ui.notification_show("No updates were successful", type="warning", duration=3)
        else:  # No edits found
            ui.notification_show("No changes to save", type="warning", duration=3)

app = App(app_ui, server)