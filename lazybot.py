# %% [markdown]
# Import libraries

# %%
import praw
import openai
import random

# %% [markdown]
# Fill in your details/api keys

# %%
# Connect openAI
openai.api_key = "openai-api-key"

# Connect Reddit
reddit = praw.Reddit(
    client_id="reddit-client-id",
    client_secret="reddit-client-secret",
    password="reddit-password",
    user_agent="reddit-ua",
    username="reddit-username",
)
reddit.read_only = True
print(f"Logged in as {reddit.user.me()}")

# %% [markdown]
# _sublist_ A list of subredits to use
#
#
# _scoremin_ The minimum score a post needs to have to be considered
#
#
# _pickRandom_ Pick a random or the post with the highest score
#
#
# _useAI_ Use ChatGPT to generate article (for safety)

# %%
sublist = ["australia", "straya", "australian"]
scoremin = 120

pickRandom = False
useAI = False

# %% [markdown]
# Get posts from subreddits

# %%
posts = []

for sub in sublist:
    for submission in reddit.subreddit(sub).hot(limit=20):
        if submission.score >= scoremin and submission.url.startswith(
            ("https://i.redd.it/", "https://www.reddit.com")
        ):
            print(submission.title)
            posts.append(submission)

print(f"Found {len(posts)} good posts")

# %% [markdown]
# Get best or random post

# %%
if pickRandom:
    # Pick a random post of the list
    pickedPost = random.choice(posts)
    pickedScore = pickedPost.score
else:
    # Pick the best post
    pickedScore = 0
    for post in posts:
        if post.score > pickedScore:
            pickedPost = post
            pickedScore = pickedPost.score

print(f"Picked: {pickedPost.title}, with a score of {pickedScore}")

# %% [markdown]
# Get the posts comments

# %%
comments = []
pickedPost.comments.replace_more(limit=4)
for comment in pickedPost.comments.list():
    if comment.score > 1:
        commentdata = {
            "score": comment.score,
            "comment": comment.body,
            "author": comment.author,
        }
        comments.append(commentdata)

comments = sorted(comments, key=lambda d: d["score"], reverse=True)

# %% [markdown]
# Generate article

# %%
promt = f"Write a newspaper article about a reddit post with the title: {pickedPost.title}, posted by {pickedPost.author}; here are some comments people made on that post: "
for comment in comments[0:5]:
    promt += f"{comment['author']} wrote { comment['comment'] }; "
print(f"Promt: {promt}")

if useAI:
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a very credible Australian journalist.",
            },
            {"role": "user", "content": promt},
        ],
    )
    reply = chat.choices[0].message.content
    print(f"Article: {reply}")
