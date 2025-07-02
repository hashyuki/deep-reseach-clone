from typing import Any, Dict, List


def resolve_urls(urls_to_resolve: List[Any], id: int) -> Dict[str, str]:
    """
    Vertex AI検索URL（非常に長い）を、各URLに一意のIDを持つ短いURLにマップを作成します。
    各元のURLが一貫した短縮形式を取得し、一意性を維持することを保証します。
    """
    prefix = "https://vertexaisearch.cloud.google.com/id/"
    urls = [site.web.uri for site in urls_to_resolve]

    # 各一意のURLを最初の出現インデックスにマップする辞書を作成
    resolved_map = {}
    for idx, url in enumerate(urls):
        if url not in resolved_map:
            resolved_map[url] = f"{prefix}{id}-{idx}"

    return resolved_map
