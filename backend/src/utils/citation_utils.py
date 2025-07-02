def insert_citation_markers(text, citations_list):
    """
    開始・終了インデックスに基づいてテキスト文字列に引用マーカーを挿入します。

    Args:
        text (str): 元のテキスト文字列
        citations_list (list): 辞書のリスト。各辞書には
                               'start_index'、'end_index'、
                               'segment_string'（挿入するマーカー）が含まれます。
                               インデックスは元のテキストに対するものとします。

    Returns:
        str: 引用マーカーが挿入されたテキスト
    """
    # end_index で降順にソート
    # end_index が同じ場合は、start_index で降順にソート
    # これにより、文字列の最後での挿入が、まだ処理が必要な
    # 文字列の前の部分のインデックスに影響を与えないことを保証します
    sorted_citations = sorted(
        citations_list, key=lambda c: (c["end_index"], c["start_index"]), reverse=True
    )

    modified_text = text
    for citation_info in sorted_citations:
        # これらのインデックスは*元の*テキストの位置を参照しますが、
        # 最後から反復処理するため、すでに処理された文字列の部分に
        # 対する挿入位置として有効なままです
        end_idx = citation_info["end_index"]
        marker_to_insert = ""
        for segment in citation_info["segments"]:
            marker_to_insert += f" [{segment['label']}]({segment['short_url']})"
        # 元の end_idx 位置に引用マーカーを挿入
        modified_text = (
            modified_text[:end_idx] + marker_to_insert + modified_text[end_idx:]
        )

    return modified_text


def get_citations(response, resolved_urls_map):
    """
    AIモデルのレスポンスから引用情報を抽出してフォーマットします。

    この関数は、レスポンスで提供されるグラウンディングメタデータを処理して
    引用オブジェクトのリストを構築します。各引用オブジェクトには、
    参照するテキストセグメントの開始・終了インデックス、および
    サポートするウェブチャンクへのフォーマット済みマークダウンリンクを
    含む文字列が含まれます。

    Args:
        response: AIモデルからのレスポンスオブジェクト。
                  `candidates[0].grounding_metadata`を含む構造を持つことが期待されます。
                  また、チャンクURIを解決済みURLにマップするために
                  `resolved_map`が利用可能であることに依存します。

    Returns:
        list: 辞書のリスト。各辞書は引用を表し、以下のキーを持ちます：
              - "start_index" (int): 元のテキストで引用されたセグメントの
                                     開始文字インデックス。
                                     指定されていない場合は0がデフォルト。
              - "end_index" (int): 引用されたセグメントの終了直後の
                                   文字インデックス（排他的）。
              - "segments" (list[str]): 各グラウンディングチャンクに対する
                                        個別のマークダウン形式のリンクのリスト。
              - "segment_string" (str): 引用のすべてのマークダウン形式の
                                        リンクを連結した文字列。
              有効な候補やグラウンディングサポートが見つからない場合、
              または必須データが欠落している場合は空のリストを返します。
    """
    citations = []

    # レスポンスと必要なネストされた構造が存在することを確認
    if not response or not response.candidates:
        return citations

    candidate = response.candidates[0]
    if (
        not hasattr(candidate, "grounding_metadata")
        or not candidate.grounding_metadata
        or not hasattr(candidate.grounding_metadata, "grounding_supports")
    ):
        return citations

    for support in candidate.grounding_metadata.grounding_supports:
        citation = {}

        # セグメント情報が存在することを確認
        if not hasattr(support, "segment") or support.segment is None:
            continue  # セグメント情報が欠落している場合はこのサポートをスキップ

        start_index = (
            support.segment.start_index
            if support.segment.start_index is not None
            else 0
        )

        # 有効なセグメントを形成するために end_index が存在することを確認
        if support.segment.end_index is None:
            continue  # end_index が欠落している場合はスキップ（必須のため）

        # スライス/範囲目的で排他的な終了とするために end_index に 1 を加算
        # (API が包括的な end_index を提供すると仮定)
        citation["start_index"] = start_index
        citation["end_index"] = support.segment.end_index

        citation["segments"] = []
        if (
            hasattr(support, "grounding_chunk_indices")
            and support.grounding_chunk_indices
        ):
            for ind in support.grounding_chunk_indices:
                try:
                    chunk = candidate.grounding_metadata.grounding_chunks[ind]
                    resolved_url = resolved_urls_map.get(chunk.web.uri, None)
                    citation["segments"].append(
                        {
                            "label": chunk.web.title.split(".")[:-1][0],
                            "short_url": resolved_url,
                            "value": chunk.web.uri,
                        }
                    )
                except (IndexError, AttributeError, NameError):
                    # chunk、web、uri、または resolved_map に問題がある場合を処理
                    # 簡単のため、この特定のセグメントリンクの追加をスキップします
                    # 本番システムでは、これをログに記録することを検討してください
                    pass
        citations.append(citation)
    return citations
