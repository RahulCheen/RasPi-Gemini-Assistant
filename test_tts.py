import os
import io
import json
import wave
import traceback
import pyaudio
import markdown
from bs4 import BeautifulSoup
import asyncio
import edge_tts
from playsound3 import playsound

import tempfile
from pathlib import Path

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        return {}

CONFIG = load_config()

class EdgeTTS:
    def __init__(self):
        self.voice = "en-GB-RyanNeural"
        self.rate = "+0%"
        self.volume = "+0%"

    async def _stream_audio(self, text):
        """
        Generate speech with edge-tts and play it using playsound.
        This function is async, but playback itself is blocking.
        """
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            volume=self.volume,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "response.mp3"

            await communicate.save(str(temp_file))

            print(f"Playing {temp_file}...")
            playsound(str(temp_file), block=True)

    def speak(self, text):
        print("Synthesizing speech (EdgeTTS)...")
        
        try:
            html_text = markdown.markdown(text)
            soup = BeautifulSoup(html_text, "html.parser")
            clean_text = soup.get_text()
            clean_text = " ".join(clean_text.split())
            
            print(f"--- Cleaned Text ({len(clean_text)} chars) ---")
            print(clean_text[:100] + "...")
            print("------------------------------------------")

        except Exception as e:
            print(f"Warning: Text cleaning failed ({e}), using raw text.")
            clean_text = text
        
        if not clean_text:
            return

        try:
            asyncio.run(self._stream_audio(clean_text))
            print("Playback complete.")
        except Exception as e:
            print(f"TTS Error: {e}")
            traceback.print_exc()

def main():
    print("Testing EdgeTTS with complex input...")
    
    fixed_text = """
Here's a simple and delicious apple pie recipe that's perfect for beginners! It focuses on straightforward steps and readily available ingredients.

**Simple Apple Pie**

This recipe uses a pre-made crust to keep things extra easy.

**Yields:** 8 servings
**Prep time:** 20 minutes
**Cook time:** 45-55 minutes

**Ingredients:**

*   1 (9-inch) unbaked pie crust (store-bought is fine!)
*   6-8 medium apples (about 2.5 lbs), peeled, cored, and sliced about 1/4-inch thick (a mix of sweet and tart apples like Honeycrisp, Fuji, Granny Smith, Gala works best)
*   1/4 cup granulated sugar (adjust to your sweetness preference and apple tartness)
*   2 tablespoons all-purpose flour (or cornstarch for thickening)
*   1 teaspoon ground cinnamon
*   1/4 teaspoon ground nutmeg (optional, but highly recommended)
*   1 tablespoon lemon juice (fresh or bottled)
*   2 tablespoons unsalted butter, cut into small pieces
*   1 large egg, beaten (for egg wash)
*   1 tablespoon sugar (for sprinkling on top)

**Equipment You'll Need:**

*   9-inch pie plate
*   Large mixing bowl
*   Peeler and knife
*   Measuring cups and spoons
*   Baking sheet (optional, to catch any drips)

**Instructions:**

1.  **Preheat Your Oven:** Preheat your oven to **400°F (200°C)**. If you're worried about drips, place a baking sheet on the bottom rack to catch any potential overflow.

2.  **Prepare the Apples:** Peel, core, and slice your apples. Place them in a large mixing bowl.

3.  **Make the Filling:**
    *   Add the 1/4 cup granulated sugar, flour (or cornstarch), cinnamon, nutmeg (if using), and lemon juice to the bowl with the apples.
    *   Gently toss everything together until the apple slices are evenly coated.

4.  **Assemble the Pie:**
    *   Carefully place the unbaked pie crust into your 9-inch pie plate. Gently press it into the bottom and up the sides.
    *   Pour the apple filling into the pie crust. Try to arrange the apple slices evenly.
    *   Dot the top of the apple filling with the small pieces of butter.

5.  **Add the Top Crust (Optional - Lattice or Full):**
    *   **For a Simple Full Top Crust:** If you have a second pie crust, you can place it over the filling. Trim any excess dough, crimp the edges of both crusts together to seal, and cut a few slits in the top crust to allow steam to escape.
    *   **For a Lattice Top (Slightly More Effort):** Roll out the second crust and cut it into strips. Weave the strips over the apple filling to create a lattice pattern. Trim and crimp the edges.
    *   **For an Open-Faced Pie (Easiest):** You can skip the top crust altogether! Just make sure the butter dots are on the filling.

6.  **Egg Wash and Sugar Sprinkle:**
    *   In a small bowl, whisk the egg. Brush this egg wash lightly over the top crust (or the edges if you're doing an open-faced pie). This will give your crust a beautiful golden-brown shine.
    *   Sprinkle the remaining 1 tablespoon of sugar evenly over the egg-washed crust.

7.  **Bake the Pie:**
    *   Place the pie on the preheated baking sheet (if using) or directly on the oven rack.
    *   Bake for **20 minutes** at 400°F (200°C).
    *   **Reduce the oven temperature to 375°F (190°C)** and continue baking for another **25-35 minutes**, or until the crust is golden brown and the filling is bubbly. You can loosely tent the pie with foil if the crust starts to brown too quickly.

8.  **Cool and Serve:**
    *   This is the hardest part! Let the pie cool on a wire rack for at least **2-3 hours** before slicing and serving. This allows the filling to set properly.
    *   Serve warm or at room temperature. It's delicious on its own or with a scoop of vanilla ice cream!

**Tips for Success:**

*   **Don't Overcrowd the Crust:** While you want a good amount of apples, don't pack them in so tightly that you can't get the top crust on (if using).
*   **Taste Your Apples:** If your apples are very tart, you might want to add a little more sugar. If they're very sweet, you might use a bit less.
*   **Don't Skip the Cooling:** Seriously, it's important for a non-runny pie!
*   **Enjoy!** The best part of baking is eating your creation!

Enjoy your simple and delicious homemade apple pie!
"""
    
    tts = EdgeTTS()
    tts.speak(fixed_text)
    print("\nTest complete.")

if __name__ == "__main__":
    main()
