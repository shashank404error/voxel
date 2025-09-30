import os
import shutil

# List of input audio file paths
input_files = [
"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/e39e7510567932dd6b5f77fea73b9104a6b2db1852ad54f259fc45ab1d14d28a/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/f47e14bfa36697a98832e1d8828a0a4a1e07beba648b8f915615e7af79b431c9/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/1250716fd8e6d0ba7556bea379b28a87dff9f6494610091d726cf1eea91921f2/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/82b770837c2ecdd4c913c09f6a8b33338255d1bf00daeb8323322bdb3d565dc7/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/c9b63fd8d43d3afc10bc54e523163f258f795ca962ae54a1407267ae83021683/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/b753fe4b1e5587f08af56fd5f7cdce1d08425840b483c86987ce0705682f5290/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/cdb86f69cf80150e0be5384d8744e636bc2a94874b225e048e5baed482084440/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/813d39789230b5078ed6bef016524eefac331f4924ceffdfb676ea9a29b1f08e/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/ef94d93772d35926d7dbf9b4594508009ad0a34345e36379a06848bd7eeeb651/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/4687d260fed811a866292a496bb25ab3e4079294636ecc9d41bdcc16cbfd96c7/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/73266b48cfc566cea2fa58a609101b3e78e48d6f3c1146e0d311203a0b4d5b7f/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/7cdc0623069839e4e4881bef96e52a88cc08c09fe95bfe1d8174952093ca5b20/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/d1848cfcf853d2c9957fc7278b4ff5a80b80cb9dd6a7e3aaf525ebcd7d6ce922/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/2a2caaa902a7a480dadba737379c76a04c7a8bd30f3ffaf5d764ac6d67da3bd4/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/ef621c131055fca8d887d06488d7418df6cdc87114459282a55b9da83345a8b6/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/d2248637d4113dac490aeb85d815114caa79454b8b5bf9d4bc3b149cbbde4647/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/088ea540452e617a55f358928c0985d971e9e5fbff2c0517fefe7c366638c621/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/cbb6bf3fc3402ffdf10cc8aca4175a9e4791208ced695492ff5702df7e32fc21/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/93da6a41235f041ea46d8153e7c99f7a26c2778973ef742b31015cd8309c4241/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/c6a3019175151cde20eddf934ff8f1b3af47900f209cc1bc8aea682e06917854/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/3f97789cf6fe4f0cded19187d220c28ff013b9e58782f70c2b212b75f83415de/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/88a7c9f33b0b7363ad59b16a52de0d2ddc30ca82da73b0c653c68c5ef97dc94a/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/4bad10764fcaa0b6ab848b4ed1039642662c938b355ce240c405440b88f1390c/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/4abf499958cb1455d6645b9ba7a5d7f1892fbe4c5b447188293116c19e6831cc/audio.wav",

"/private/var/folders/_f/6mh6x2yx0k92qxn7pz1ytmj00000gn/T/gradio/7308d35049e47607c0f52d234565207ba065cd154eee43bed6c79cb2b16453e1/audio.wav"
]

# Output directory
output_dir = "/Users/shashank404error/Desktop/weekend_projects/voxel/chatterbox/speech_variation_test/part_audio"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Copy files with new names 0.wav, 1.wav, ...
for i, file_path in enumerate(input_files):
    if os.path.exists(file_path):
        new_name = os.path.join(output_dir, f"{i}.wav")
        shutil.copy(file_path, new_name)
        print(f"Copied: {file_path} -> {new_name}")
    else:
        print(f"File not found: {file_path}")
