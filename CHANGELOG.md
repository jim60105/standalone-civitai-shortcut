# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.6.7] - 2023-09-18

### Changed
- Changed the names of each menu to correspond to their functions

## [1.6.6] - 2023-09-07

### Changed
- In Prompt Recipe, deselected the option 'Delete from references when selecting a thumbnail'
- When clicking on a model within the references in Prompt Recipe, it now displays brief information on the top instead of navigating to the model information
- In classification, deselected the option 'Delete from classification when selecting a thumbnail'
- When clicking on a model within the classification, it now displays brief information on the right instead of navigating to the model information

### Added
- Added feature in Prompt Recipe to input directives in the prompt based on the type of the selected reference model

## [1.6.5] - 2023-09-04

### Changed
- Updated compatibility with gradio version 3.41.2 or higher
- Requires the latest update of A1111 to function correctly

## [1.6.4] - 2023-08-19

### Added
- Save available model data in SDUI's LoRa metadata editor (only if no existing data)
- Added feature to Assistance->Scan and Update Models for generating missing LoRa metadata files

### Changed
- Changed the names of some menus

## [1.6.3] - 2023-08-10

### Changed
- Modified the interface of the classification
- Modified shortcut information to include the respective shortcut as the default reference model when sending a prompt from the image to the recipe

### Added
- Added shortcut browser feature to the classification, improving convenience

## [1.6.2] - 2023-08-03

### Added
- Update the registration date of the shortcut (perform Assistance->Update Shortcuts: Update the model information for the shortcut for existing data)

### Changed
- Intuitively modified the settings of the gallery

## [1.6.1] - 2023-07-31

### Changed
- Modified the interface of the reference shortcut model in the recipe
- When generating thumbnails automatically, the model with the lowest NSFW level (most safe for work) will be selected
- The NSFW filter will now operate across all ranges
- In the classification, display the removed models among the shortcut models

## [1.6.0] - 2023-07-29

### Added
- Added NSFW Filter function
- Added a tab to register reference models in the prompt recipe
- Added a setting in the shortcut browser to allow users to change the position of the search bar to their desired location, either above or below the thumbnail list

### Changed
- Revamped prompt recipe
- Enhanced the search function for prompt recipes

## [1.5.8] - 2023-07-27

### Added
- Added a 'Personal Note' section to the model information, and made it searchable using '@' in the search

## [1.5.7] - 2023-07-18

### Added
- Added functionality to filter using the base model provided by Civitai

### Changed
- Changed the classification categories to be selected from a dropdown list instead of searching in the search section
- Selected classification categories will work as an 'AND' operation, meaning they will function as an intersection
- Improved management of shortcuts that are classified under multiple categories

## [1.5.6] - 2023-07-14

### Changed
- Changed the "user gallery paging" method to cursor-based paging as recommended by Civitai

## [1.5.5] - 2023-07-09

### Changed
- When downloading a file, if there is no primary file in the download list, it will be modified to not generate version info and preview images. Only the corresponding file will be downloaded
- The download file list will indicate whether it is a primary file
- Modified the sorting so that the shortcuts are sorted based on the 'name' field

## [1.5.4] - 2023-06-05

### Added
- Added a feature to suggest available names for the model download folder (listed in the order of model name, author, and model tag)

### Changed
- Modified the prompt recipe to update only the current state of the prompt content when dropping an image, without generating a new recipe
- When the shortcut is selected, the information will load only in the selected tab
- Modified to search for the model information used in the User Gallery screen from the downloaded model information
- Retrieve only image information in real-time from the user gallery images on the Civitai website (expected reduction in ASGI application errors)

### Fixed
- Corrected a typo

## [1.5.3] - 2023-05-31

### Added
- Added the ability to change the file name of the model file to be downloaded
- When clicking on the file name, an input field appears to allow changing the file name

### Changed
- Changed to allow selection only through checkboxes when choosing files
- Changed the behavior during file downloads to prevent the download of info and preview images when there is no download file available
- Changed the search criteria for Scan Models
- Modified the size of the thumbnail image to be smaller
- Modified the thumbnail image to be changeable

### Fixed
- Fixed Shortcut Browser screen ratio error

## [1.5.2] - 2023-05-28

### Added
- Added description/modified the wording for folder creation during model download

### Changed
- Changed the position of Prompt Recipe (Assistance -> Top level)
- Changed the position of Scan and Update Models (Manage -> Assistance)

## [1.5.1] - 2023-05-26

### Added
- Added the feature to change the preview image in the model information tab -> images: Change Preview Image button (only appears if the model has been downloaded)

### Changed
- For downloaded models, updated the default folder name displayed to be the downloaded folder information (may have inaccuracies if the model is downloaded in more than one location)
- In the Downloaded Model Information Tab, you can view the downloaded location and files

## [1.5.0] - 2023-05-24

### Added
- Added the Assistance tab
- Added new feature called Prompt Recipe
- Added 'Create' button that appears only when [New Classification] or [New Prompt Recipe] is selected
- Added folder named 'sc_recipe' to store the images for the Prompt Recipe
- Added new option 'Disable Classification Gallery Preview Mode' under 'Manage -> Settings -> Options'

### Changed
- Merged the information tab and the saved model information tab in the Civitai model
- Removed the Civitai model information that used to fetch real-time information from the Civitai site
- Updated shortcut information registered during Stable Diffusion startup (can be enabled or disabled in manage->setting->option)
- Moved the classification feature to the Assistance tab
- Registration URLs are now stored in the CivitaiShortCutBackupUrl.json file in the format {url: name}
- File is automatically generated and updated when performing 'Update the model information for the shortcut' or when the automatic update feature is enabled

### Removed
- Removed the 'sc_saved' folder which was used to backup the registration URLs for shortcuts

### Fixed
- Bug: Issue in the prompt recipe where the saved image loses the generated image information (appears to be a problem with the Gradio Image component)

## [1.4.1] - 2023-05-13

### Added
- Added "Reload UI" button that reloads the SDUI
- Added new option to set the download folder location for LyCORIS in "Download Folder for Extensions" settings

### Changed
- Changed the interface design
- Provided more detailed information about the file to be downloaded
- Modified some design and functionality in the Manage -> Classification section
- Integrated the create, modify, delete, and update functions for classification with the "Shortcut Item" section on the left
- Added the "Screen Style" option to Manage -> Setting to adjust the ratio between Shortcut Browser and Information Tab
- Modified the internal format of the uploaded files in the Upload section to recognize "url=civitai model url" format

### Fixed
- Fixed issue where drag & drop feature in Upload does not work properly in Linux environment

### Security
- Note: Please use the "Save Setting" button for saving settings as the "Reload UI" button does not include this feature

## [1.4.0] - 2023-05-11

### Added
- Added new tab called "Downloaded Model Information" to the Information tab
- Added ability to view information about currently downloaded files
- Added list of versions of the downloaded model with detailed information
- Added ability to view Civitai-provided information for versions in JSON format
- Added "Open Download Image Folder" function
- Added "Open Saved Information Folder" function
- Added ability to set the display style of the Shortcut Browser ("Manage->Setting->Shortcut Browser and Information Images: Shortcut Browser Thumbnail Count per Page")

### Changed
- All "Open Folder" functions only work when the folder exists
- If you set Shortcut Browser Thumbnail Count per Page to 0, the entire list will be displayed as before

## [1.3.5] - 2023-05-07

### Added
- Added ability to specify the folder to download to
- Added ability to set user-defined classification item as the download item for the model
- Added "Create Model Name Folder" option
- Added ability to set the number of images to download when registering a shortcut

### Changed
- Changed the rules and methods for downloading the model
- Image downloads are now downloaded by default to outputs/download-images
- Changed the display type of thumbnail images
- If you set user-defined classification item as download item, you cannot create subfolders
- Downloaded model files can be freely moved to any desired folder
- The "-" character will be replaced when creating folders

## [1.3.3] - 2023-05-01

### Added
- Added "Scan and Update Models" and "Settings" tabs to the Manage tab
- Added Scan Models for Civitai function
- Added Update Shortcut function (moved from Upload tab)
- Added Update the model information for the shortcut function
- Added Scan downloaded models for shortcut registration function
- Added Download Folder for Extensions setting

### Changed
- Changed the name of the model info file that records information about the model
- Set the number of columns in the image gallery (Shortcut Browser and Information Images, User Gallery Images)

## [1.3.1] - 2023-04-28

### Added
- Added new feature to manage and classify items
- Added ability to add, delete, and update classification items in the "manage" -> "classification" tab
- Added "model classification" item in the "civitai shortcut" -> "information" tab
- Added classification items to the browsing "search" feature
- Added ability to use "@" prefix to enter multiple classification items

### Changed
- Classification items can be selected from dropdown list and work with "filter model type" and "search" features
- Tags, classification, and search keywords are applied with "and" operation, and each item is applied with "or" operation

## [1.2.1] - 2023-04-18

### Changed
- Modified the application method for generating image information to include information from Civitai's 'information' field
- Changed the naming convention for saved images

### Removed
- Removed the Downloaded Model tab which duplicated the functionality of the Saved Model Information tab

## [1.2.0] - 2023-04-20

### Added
- Added Civitai User Gallery tab where users can view the information and images of the models in the gallery
- Added "Update Downloaded Model Information" button below the "Upload" button
- Added ability to specify the folder name when downloading a model to an individual folder

### Changed
- Default format for folder names is "model name-version name" but users can input their preferred value
- Made minor design changes

### Removed
- Removed the option to download additional networks by selecting them from a list

### Fixed
- Bug: When viewing the gallery images at full size, the image control and browsing controls overlap

## [1.1.3] - 2023-04-15

### Added
- Added #tag search feature to the search function
- Added tag search functionality to shortcut storage

### Changed
- Took measures to alleviate bottleneck issues during information loading
- Search terms are separated by commas and connected with "or" operation within search terms and tags, with "and" operation between search terms and tags
- Existing shortcuts require "update shortcut model information" for tag searches

## [1.1.0] - 2023-04-14

### Added
- Added separate folder for saving model information and images when registering a shortcut
- Added "Update Shortcut's Model Information" button to keep model information and images up to date
- Added "Update Model Information" button to "Saved Model Information" Tab for individual updating

### Changed
- Users can now access model information from "Saved Model Information" Tab even without connection to Civitai site
- Moved "Delete shortcut" button to "Saved Model Information" Tab

### Removed
- Removed "Thumbnail Update" button
- Removed "Download images Only" button from "Civitai Model Information" Tab

---

[Unreleased]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.7...HEAD
[1.6.7]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.6...v1.6.7
[1.6.6]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.5...v1.6.6
[1.6.5]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.4...v1.6.5
[1.6.4]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.3...v1.6.4
[1.6.3]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.2...v1.6.3
[1.6.2]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.8...v1.6.0
[1.5.8]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.7...v1.5.8
[1.5.7]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.6...v1.5.7
[1.5.6]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.5...v1.5.6
[1.5.5]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.4...v1.5.5
[1.5.4]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.3...v1.5.4
[1.5.3]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.2...v1.5.3
[1.5.2]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.3.5...v1.4.0
[1.3.5]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.3.3...v1.3.5
[1.3.3]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.3.1...v1.3.3
[1.3.1]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.2.1...v1.3.1
[1.2.1]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.1.3...v1.2.0
[1.1.3]: https://github.com/jim60105/standalone-civitai-shortcut/compare/v1.1.0...v1.1.3
[1.1.0]: https://github.com/jim60105/standalone-civitai-shortcut/releases/tag/v1.1.0
