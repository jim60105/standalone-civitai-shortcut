# Personal reasons make it difficult for further updates. Feel free to use the source without any restrictions. I sincerely apologize.

# This update is compatible with gradio version 3.41.2 or higher. It requires the latest update of A1111 to function correctly.

# Civitai Shortcut

Stable Diffusion Webui Extension for Civitai, to download civitai shortcut and models.

# Install

Stable Diffusion Webui's Extension tab, go to Install from url sub-tab. Copy this project's url into it, click install.

    git clone https://github.com/sunnyark/civitai-shortcut

# Usage instructions

![screenshot 2023-09-15 203613](https://github.com/sunnyark/civitai-shortcut/assets/40237431/fdac59c0-0ced-41fb-8faa-83029b3ffc3f)

* Upload : This function creates a shortcut that can be used by the extension when you enter the Civitai site's model URL. It only works when the site is functioning properly. You can either click and drag the URL from the address bar or drag and drop saved internet shortcuts. You can also select multiple internet shortcuts and drop them at once.
* Model Browsing : "This feature displays registered models in thumbnail format and, upon selection, shows detailed information about the model on the right side of the window.
* Scan New Version : This is a function that searches for the latest version of downloaded models on the Civitai site. It retrieves information from the site and only functions properly when the site is operational.

![register_model_direct](https://github.com/sunnyark/civitai-shortcut/assets/40237431/c6db4ced-9cec-4488-ac3f-9a17fadb42b8)

![register_model_shortcut](https://github.com/sunnyark/civitai-shortcut/assets/40237431/a18cc188-0d7a-4860-91fa-b9b2b27f4bdc)

* Prompt Recipe : The Prompt Recipe feature allows you to register and manage frequently used prompts.

![screenshot 2023-09-15 201815](https://github.com/sunnyark/civitai-shortcut/assets/40237431/d3d61c0a-c749-40ee-bc8c-69c35e9c6ba7)

![screenshot 2023-09-15 201833](https://github.com/sunnyark/civitai-shortcut/assets/40237431/773dc92f-3fd5-4509-94bb-99a9e50bec34)

![screenshot 2023-09-15 201853](https://github.com/sunnyark/civitai-shortcut/assets/40237431/ecf6e1a7-59f8-4eb5-a58f-5a7ff7824437)

* Assistance

1. Classification : Function for managing shortcuts by classification.

![screenshot 2023-09-15 201933](https://github.com/sunnyark/civitai-shortcut/assets/40237431/7881d3d8-d2a3-4502-b39c-fb40a17cf21c)

![screenshot 2023-09-15 201956](https://github.com/sunnyark/civitai-shortcut/assets/40237431/94b2b2a1-f148-42dc-b6a8-21c1381dc55f)

![screenshot 2023-09-15 202004](https://github.com/sunnyark/civitai-shortcut/assets/40237431/9003d94d-5a13-4613-9fa6-722b1e892874)

2. Scan and Update Models
   Scan Models - Scan and register shortcut for models without model information that are currently held.
   Update Shortcut - Move the shortcut update function from the Upload tab.
   Update the model information for the shortcut - Update the information of registered shortcuts with the latest information.
   Scan downloaded models for shortcut registration - Register new shortcuts for downloaded models that have been deleted or have missing model information.

![screenshot 2023-09-15 202018](https://github.com/sunnyark/civitai-shortcut/assets/40237431/7f200d24-a4ca-4e23-834a-71470590ee49)

* Setting tab - Set the number of columns in the image gallery.

![screenshot 2023-09-15 202037](https://github.com/sunnyark/civitai-shortcut/assets/40237431/67e2e7c5-0cd6-4917-a4c8-b9ffb45832f9)

# Features

You can save the model URL of the Civitai site for future reference and storage.
This allows you to download the model when needed and check if the model has been updated to the latest version.
The downloaded models are saved to the designated storage location.

# Notice

Four folders and five JSON files will be created, each serving the following roles.

* sc_recipes : Folder where Prompt Recipe images are saved.
* sc_gallery : Folder for caching images in the User Gallery.
* sc_thumb_images : Folder where thumbnails are saved.
* sc_infos : Folder where model information and images are saved upon registration.
* CivitaiShortCut.json : JSON file for recording and managing registered model URLs.
* CivitaiShortCutClassification.json: JSON file for managing classification categories.
* CivitaiShortCutSetting.json: JSON file for storing configuration settings.
* CivitaiShortCutRecipeCollection.json : JSON file for managing data related to Prompt Recipes.
* CivitaiShortCutBackupUrl.json : JSON file for backing up the URL during shortcut registration.
