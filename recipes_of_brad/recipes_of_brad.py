import reflex as rx
import json
from recipes_of_brad.vision import get_response

with open("data/results.json") as f:
    data = json.load(f)

def calculate_similarity(list1, list2):
    count = 0
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                count += 5
                break
            elif item1 in item2 or item2 in item1:
                count += 1
                break
    return count

class State(rx.State):
    img: str
    ingredients: list
    ingredients_str: str
    upload_progress: int
    is_uploading: bool = False

    results: list[dict] = []

    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        yield rx.clear_selected_files("upload1")

        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.filename

            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            self.img = file.filename

            self.ingredients = get_response(outfile)
            if not self.ingredients or len(self.ingredients) == 0:
                self.is_uploading = False
                return

            self.ingredients_str = ", ".join(self.ingredients)


            results_temp = []

            for d in data:
                try:
                    d["ingredient"] = list(set(d["ingredient"]))
                    d["seasoning"] = list(set(d["seasoning"]))
                    d["ingredient_str"] = ", ".join(d["ingredient"])
                    d["seasoning_str"] = ", ".join(d["seasoning"])

                    score = calculate_similarity(self.ingredients, d["ingredient"])

                    if score >= 2:
                        d["score"] = score
                        d["thumbnail"] = d["thumbnails"]["standard"]["url"]
                        results_temp.append(d)
                except Exception as e:
                    print("ERROR", e, d)
                    break

            self.results = sorted(results_temp, key=lambda x: x["score"], reverse=True)[:10]

            self.is_uploading = False

            break



color = "rgb(107,99,246)"

def show_recipes(recipe):
     return rx.table.row(
        rx.table.cell(
            rx.link(
                rx.vstack(
                    rx.image(src=recipe["thumbnail"]),
                    rx.heading(recipe["food"], size="2"),
                    align_items="center",
                ),
                href=f"https://www.youtube.com/watch?v={recipe['video_id']}",
                target="_blank",
            ),
        ),
        rx.table.cell(
            rx.text(recipe["ingredient_str"]),
        ),
        rx.table.cell(recipe["seasoning_str"]),
        rx.table.cell(recipe["score"]),
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("빵형의 레시피"),
            rx.upload(
                rx.vstack(
                    rx.button("Select a photo", color=color, bg="white", border=f"1px solid {color}"),
                    rx.text("Or drop here!"),
                    rx.hstack(rx.foreach(rx.selected_files("upload1"), rx.text)),
                    align_items="center",
                ),
                # Auto upload
                rx.moment(
                    interval=rx.cond(
                        rx.selected_files("upload1") & ~State.is_uploading,
                        500,
                        0,
                    ),
                    on_change=lambda _: State.handle_upload(rx.upload_files(upload_id="upload1")),
                    display="none",
                ),
                max_files=1,
                multiple=False,
                accept={
                    "image/png": [".png"],
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/gif": [".gif"],
                    "image/webp": [".webp"],
                },
                id="upload1",
                border=f"1px dotted {color}",
                padding="2em",
            ),

            rx.hstack(
                rx.cond(
                    State.is_uploading,
                    rx.chakra.circular_progress(is_indeterminate=True),
                    None
                ),
                rx.cond(
                    State.img,
                    rx.box(rx.image(src=rx.get_upload_url(State.img), height="5em")),
                    None
                ),
                rx.box(rx.text(State.ingredients_str)),
            ),

            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("영상"),
                        rx.table.column_header_cell("재료"),
                        rx.table.column_header_cell("양념/조미료"),
                        rx.table.column_header_cell("유사도"),
                    ),
                ),
                rx.table.body(rx.foreach(State.results, show_recipes)),
            ),
            padding_top="5em",
            align_items="center",
        ),

    )

app = rx.App()
app.add_page(index, title="🍞빵형의 레시피")
