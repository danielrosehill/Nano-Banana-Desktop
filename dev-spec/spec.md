# First Development Specification

The purpose of this utility will be to suport AI image editing using Gemini's image to image modality.

 The image editor should use a tab based layout: the filename appears as the title to the tab and the user can click tabs to navigate between them. 

 ## Prompts 

 The interface should support:

 - Using prewritten prompts (in isolation or combination)
 - Using custom prompts 

The initial implementation should follow this workflow: edits are applied by sending the current version to Gemini with the editing prompt. 

In other words:

- If a user opens an image and then applies one prompt: 
- The new file created loads in the viewfinder, taking the place of the initial image 
- If the user makes subsequent changes, then the logic is: image 2 + prompts to Gemini. Image 3 is returned. This process repeats iteratively.

## File Handling 

Implement this logic which is intended to provide a mechanism for backup and version control:

- If the user opens a file a.png whose path is foo/a.png

Then:

- A folder is created at foo/a 
- a.png is moved into that folder at foo/a/original.png (etc). 
- The first version which Gemini returns is saved at foo/a/v1.png - increasingly iteratively through versioning 

Versions are displayed on the frontend as thumbnail previews. Previews are dynamically generated as data is received from Gemini and new versions are iterated. 

## Prompt Construction 

The initial prompt library (at prompts) will consist of a handful of commonplace image to image edits. 

The API call construction logic should implement the versatility of prompting as an editing method: multiple prompts can be chained and so long as the cumulative text does not exceed the input limit (in this use case almost impossible) the image will be regenerated on the basis of these prompts.

The following prompting methods should be supported. The prompts should be implemented on the frontend as buttons:

- User provides one prewritten prompt: then, only that prompt gets sent with the image (or version) to Gemini for inpainting. 
- User selects multiple prewritten prompts: the prompts are injected into a template and formatted by upper case sections used to separate between instructions.

An example of a constructed prompt with multiple elements might be:

"Please apply the following edits to this image:

SATURATION

Equalise the saturation.

BLUR

Apply a subtle background blur to increase the prominence of the subject from the background."

In this example SATURATION and BLUR might be the names of stored template prompts with an upper case transform applied for emphasis. 

## Custom Prompt Handling

The following two prompt editing templates should be supported:

- Custom prompt: The user uses a free text element to provide their own prompt for editing. 
- Custom + templated: The user writes a  custom prompt and also selects templated prompts. These should be dynamically constructed but the user prompt should come before the templated prompts

## Version Selection 

The app should account for a common problem when using tools like Nano Banana for inpainting: commonly one iteration is poor and undesired. 

To support this the app should implement a discard button. Pressing it: deletes the iteration from the filesystem; triggers loading of the previous iteration from the filesystem; if there is no previous iteration, the original loads.

## Resolution Handling

By default, "sync" is used - subject resolution is output. 

However, the user should also be able to select a desired resolution from: 1:1, 16:9, 21:9, 9:16. 

## Data Persistence 

The user will want to use the app frequently so the app should implement a mechanism for storing the gemini API key in local storage (folllowing security best practices) and also support updating the API key and in turn updating the backend store. 