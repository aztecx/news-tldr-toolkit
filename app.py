import streamlit as st

from src.summariser import NewsSummariser
from summarise_url import fetch_page_text
from news_digest import RSS_FEEDS, fetch_feed_items


def render_url_mode() -> None:
    st.header("🔗 Summarise a URL")

    url = st.text_input(
        "Article URL",
        placeholder="https://www.bbc.co.uk/news/...",
    )

    max_chars = st.slider(
        "Approximate maximum length of TL;DR (characters)",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
    )

    if st.button("Summarise URL"):
        if not url.strip():
            st.warning("Please enter a URL.")
            return

        with st.spinner("Fetching and summarising article..."):
            try:
                page_text = fetch_page_text(url)
            except Exception as e:
                st.error(f"Error fetching URL: {e}")
                return

            if not page_text:
                st.error("Could not extract any text from the page.")
                return

            summariser = NewsSummariser()
            result = summariser.summarise(page_text, max_chars=max_chars)

        st.subheader("TL;DR")
        st.write(result.tldr)

        st.subheader("Bullet Points")
        if result.bullet_points:
            for i, bullet in enumerate(result.bullet_points, start=1):
                st.markdown(f"- **{i}.** {bullet}")
        else:
            st.write("_No bullet points generated._")


def render_file_mode() -> None:
    st.header("📄 Summarise a local file")

    uploaded_file = st.file_uploader(
        "Upload a text file (.txt or .md)",
        type=["txt", "md"],
    )

    max_chars = st.slider(
        "Approximate maximum length of TL;DR (characters)",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        key="file_max_chars",
    )

    if st.button("Summarise file"):
        if uploaded_file is None:
            st.warning("Please upload a file first.")
            return

        try:
            # uploaded_file is a BytesIO-like object
            file_bytes = uploaded_file.read()
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return

        text = text.strip()
        if not text:
            st.error("The uploaded file seems to be empty or unreadable.")
            return

        with st.spinner("Summarising file..."):
            summariser = NewsSummariser()
            result = summariser.summarise(text, max_chars=max_chars)

        st.subheader("TL;DR")
        st.write(result.tldr)

        st.subheader("Bullet Points")
        if result.bullet_points:
            for i, bullet in enumerate(result.bullet_points, start=1):
                st.markdown(f"- **{i}.** {bullet}")
        else:
            st.write("_No bullet points generated._")



def render_digest_mode() -> None:
    st.header("📰 News digest by keyword")

    query = st.text_input(
        "Keyword or phrase",
        placeholder="e.g. Colchester, France, NHS, AI in Ipswich",
    )

    max_articles = st.slider(
        "Maximum number of articles to summarise",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
    )

    max_chars = st.slider(
        "Approximate maximum length of TL;DR (characters)",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        key="digest_max_chars",
    )

    if st.button("Run news digest"):
        query_clean = (query or "").strip()
        if not query_clean:
            st.warning("Please enter a keyword or phrase.")
            return

        st.write(f"Searching news feeds for: **{query_clean!r}**")

        with st.spinner("Fetching feeds and searching for matching items..."):
            # Collect items from all feeds (reuse your RSS_FEEDS + fetch_feed_items)
            all_items = []
            for feed_url in RSS_FEEDS:
                items = fetch_feed_items(feed_url)
                all_items.extend(items)

            query_lower = query_clean.lower()
            matching_items = []
            for item in all_items:
                haystack = (item.get("title", "") + " " + item.get("description", "")).lower()
                if query_lower in haystack:
                    matching_items.append(item)

        if not matching_items:
            st.info(
                f"No items matched query **{query_clean!r}** "
                f"in the current feeds. Try a broader term (e.g. 'UK', 'police', 'election')."
            )
            # Optional: show a few recent titles so user sees what's there
            if all_items:
                st.write("Here are a few recent headlines from the feeds:")
                for item in all_items[:5]:
                    st.markdown(f"- {item.get('title', '').strip()}")
            return

        st.success(f"Found {len(matching_items)} matching items. Showing up to {max_articles}.")

        summariser = NewsSummariser()

        for i, item in enumerate(matching_items[:max_articles], start=1):
            title = item.get("title", "").strip()
            link = item.get("link", "").strip()

            with st.expander(f"Article {i}: {title}", expanded=(i == 1)):
                if link:
                    st.markdown(f"[Read full article]({link})")

                with st.spinner("Fetching and summarising article..."):
                    try:
                        page_text = fetch_page_text(link) if link else ""
                    except Exception as e:
                        st.error(f"Error fetching article text: {e}")
                        continue

                    if not page_text:
                        st.error("Could not extract text from this article.")
                        continue

                    result = summariser.summarise(page_text, max_chars=max_chars)

                st.subheader("TL;DR")
                st.write(result.tldr)

                st.subheader("Bullet Points")
                if result.bullet_points:
                    for j, bullet in enumerate(result.bullet_points, start=1):
                        st.markdown(f"- **{j}.** {bullet}")
                else:
                    st.write("_No bullet points generated._")



def main() -> None:
    st.set_page_config(page_title="News TL;DR Toolkit", page_icon="📰")

    st.title("News TL;DR Toolkit")
    st.write(
        "Summarise news articles using a local transformer model.\n\n"
        "Use the options below to switch between different tools."
    )

    mode = st.radio(
        "Choose a mode:",
        ["Summarise URL", "Summarise file", "News digest"],
    )

    st.write("---")

    if mode == "Summarise URL":
        render_url_mode()
    elif mode == "Summarise file":
        render_file_mode()
    elif mode == "News digest":
        render_digest_mode()


if __name__ == "__main__":
    main()
