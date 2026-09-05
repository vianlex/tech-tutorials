---
title: Release assets with an explicit base
description: Asset tables can remain useful outside release pages without inventing version facts.
outputs: [HTML, markdown]
---

{{< release-assets base="https://downloads.example.org/releases/stable" algo="sha256" >}}
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  docs-linux-amd64.tar.gz
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  Docs manual (final).zip
{{< /release-assets >}}
