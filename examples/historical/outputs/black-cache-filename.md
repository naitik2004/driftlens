# DriftLens

**3 finding(s)** across 1 code change(s). Advisory analysis.

Base: `a9d8af466a65b7d88ea35e0ff4c460175098260e`  
Head: `36d3c516d3c09fc5f05c420900dd6b854e3c8bbd`

## black.get_cache_file: the documented filename&#x27;s 2 numeric fields are incompatible with the new declared key, which joins at least 5 dot-separated components.

**README.md:884-884** ([source](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/README.md#L884))

<blockquote>* Windows: &#96;C:\\Users\&lt;username&gt;\AppData\Local\black\black\Cache\&lt;version&gt;\cache.&lt;line-length&gt;.&lt;file-mode&gt;.pickle&#96;</blockquote>

Character offsets: 35025–35139 (end exclusive).

Update the documented filename layout to describe the new composite key; review its fields rather than guessing runtime values.

Evidence: deterministic.

[Before code](https://github.com/psf/black/blob/a9d8af466a65b7d88ea35e0ff4c460175098260e/black.py#L3601-L3602)

[After code](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/black.py#L3700-L3701)

<details><summary>Responsible change</summary>

<pre>@@ -111,32 +112,86 @@ class Changed(Enum):
     YES = 2
 
 
-class FileMode(Flag):
-    AUTO_DETECT = 0
-    PYTHON36 = 1
-    PYI = 2
-    NO_STRING_NORMALIZATION = 4
-    NO_NUMERIC_UNDERSCORE_NORMALIZATION = 8
+class TargetVersion(Enum):
+    PYPY35 = 1
+    CPY27 = 2
+    CPY33 = 3
+    CPY34 = 4
+    CPY35 = 5
+    CPY36 = 6
+    CPY37 = 7
+    CPY38 = 8
+
+    def is_python2(self) -&gt; bool:
+        return self is TargetVersion.CPY27
+
+
+PY36_VERSIONS = {TargetVersion.CPY36, TargetVersion.CPY37, TargetVersion.CPY38}
+
+
+class Feature(Enum):
+    # All string literals are unicode
+    UNICODE_LITERALS = 1
+    F_STRINGS = 2
+    NUMERIC_UNDERSCORES = 3
+    TRAILING_COMMA = 4
+
+
+VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {
+    TargetVersion.CPY27: set(),
+    TargetVersion.PYPY35: {Feature.UNICODE_LITERALS, Feature.F_STRINGS},
+    TargetVersion.CPY33: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY34: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY35: {Feature.UNICODE_LITERALS, Feature.TRAILING_COMMA},
+    TargetVersion.CPY36: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY37: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY38: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+}
 
-    @classmethod
-    def from_configuration(
-        cls,
-        *,
-        py36: bool,
-        pyi: bool,
-        skip_string_normalization: bool,
-        skip_numeric_underscore_normalization: bool,
-    ) -&gt; &quot;FileMode&quot;:
-        mode = cls.AUTO_DETECT
-        if py36:
-            mode |= cls.PYTHON36
-        if pyi:
-            mode |= cls.PYI
-        if skip_string_normalization:
-            mode |= cls.NO_STRING_NORMALIZATION
-        if skip_numeric_underscore_normalization:
-            mode |= cls.NO_NUMERIC_UNDERSCORE_NORMALIZATION
-        return mode
+
+@dataclass
+class FileMode:
+    target_versions: Set[TargetVersion] = Factory(set)
+    line_length: int = DEFAULT_LINE_LENGTH
+    numeric_underscore_normalization: bool = True
+    string_normalization: bool = True
+    is_pyi: bool = False
+
+    def get_cache_key(self) -&gt; str:
+        if self.target_versions:
+            version_str = &quot;,&quot;.join(
+                str(version.value)
+                for version in sorted(self.target_versions, key=lambda v: v.value)
+            )
+        else:
+            version_str = &quot;-&quot;
+        parts = [
+            version_str,
+            str(self.line_length),
+            str(int(self.numeric_underscore_normalization)),
+            str(int(self.string_normalization)),
+            str(int(self.is_pyi)),
+        ]
+        return &quot;.&quot;.join(parts)
+
+
+def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -&gt; bool:
+    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)
 
 
 def read_pyproject_toml(
</pre>

</details>

<details><summary>Responsible change</summary>

<pre>@@ -3598,16 +3697,16 @@ def can_omit_invisible_parens(line: Line, line_length: int) -&gt; bool:
     return False
 
 
-def get_cache_file(line_length: int, mode: FileMode) -&gt; Path:
-    return CACHE_DIR / f&quot;cache.{line_length}.{mode.value}.pickle&quot;
+def get_cache_file(mode: FileMode) -&gt; Path:
+    return CACHE_DIR / f&quot;cache.{mode.get_cache_key()}.pickle&quot;
 
 
-def read_cache(line_length: int, mode: FileMode) -&gt; Cache:
+def read_cache(mode: FileMode) -&gt; Cache:
     &quot;&quot;&quot;Read the cache if it exists and is well formed.
 
     If it is not well formed, the call to write_cache later should resolve the issue.
     &quot;&quot;&quot;
-    cache_file = get_cache_file(line_length, mode)
+    cache_file = get_cache_file(mode)
     if not cache_file.exists():
         return {}
 
</pre>

</details>

**README.md:885-885** ([source](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/README.md#L885))

<blockquote>* macOS: &#96;/Users/&lt;username&gt;/Library/Caches/black/&lt;version&gt;/cache.&lt;line-length&gt;.&lt;file-mode&gt;.pickle&#96;</blockquote>

Character offsets: 35140–35238 (end exclusive).

Update the documented filename layout to describe the new composite key; review its fields rather than guessing runtime values.

Evidence: deterministic.

[Before code](https://github.com/psf/black/blob/a9d8af466a65b7d88ea35e0ff4c460175098260e/black.py#L3601-L3602)

[After code](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/black.py#L3700-L3701)

<details><summary>Responsible change</summary>

<pre>@@ -111,32 +112,86 @@ class Changed(Enum):
     YES = 2
 
 
-class FileMode(Flag):
-    AUTO_DETECT = 0
-    PYTHON36 = 1
-    PYI = 2
-    NO_STRING_NORMALIZATION = 4
-    NO_NUMERIC_UNDERSCORE_NORMALIZATION = 8
+class TargetVersion(Enum):
+    PYPY35 = 1
+    CPY27 = 2
+    CPY33 = 3
+    CPY34 = 4
+    CPY35 = 5
+    CPY36 = 6
+    CPY37 = 7
+    CPY38 = 8
+
+    def is_python2(self) -&gt; bool:
+        return self is TargetVersion.CPY27
+
+
+PY36_VERSIONS = {TargetVersion.CPY36, TargetVersion.CPY37, TargetVersion.CPY38}
+
+
+class Feature(Enum):
+    # All string literals are unicode
+    UNICODE_LITERALS = 1
+    F_STRINGS = 2
+    NUMERIC_UNDERSCORES = 3
+    TRAILING_COMMA = 4
+
+
+VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {
+    TargetVersion.CPY27: set(),
+    TargetVersion.PYPY35: {Feature.UNICODE_LITERALS, Feature.F_STRINGS},
+    TargetVersion.CPY33: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY34: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY35: {Feature.UNICODE_LITERALS, Feature.TRAILING_COMMA},
+    TargetVersion.CPY36: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY37: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY38: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+}
 
-    @classmethod
-    def from_configuration(
-        cls,
-        *,
-        py36: bool,
-        pyi: bool,
-        skip_string_normalization: bool,
-        skip_numeric_underscore_normalization: bool,
-    ) -&gt; &quot;FileMode&quot;:
-        mode = cls.AUTO_DETECT
-        if py36:
-            mode |= cls.PYTHON36
-        if pyi:
-            mode |= cls.PYI
-        if skip_string_normalization:
-            mode |= cls.NO_STRING_NORMALIZATION
-        if skip_numeric_underscore_normalization:
-            mode |= cls.NO_NUMERIC_UNDERSCORE_NORMALIZATION
-        return mode
+
+@dataclass
+class FileMode:
+    target_versions: Set[TargetVersion] = Factory(set)
+    line_length: int = DEFAULT_LINE_LENGTH
+    numeric_underscore_normalization: bool = True
+    string_normalization: bool = True
+    is_pyi: bool = False
+
+    def get_cache_key(self) -&gt; str:
+        if self.target_versions:
+            version_str = &quot;,&quot;.join(
+                str(version.value)
+                for version in sorted(self.target_versions, key=lambda v: v.value)
+            )
+        else:
+            version_str = &quot;-&quot;
+        parts = [
+            version_str,
+            str(self.line_length),
+            str(int(self.numeric_underscore_normalization)),
+            str(int(self.string_normalization)),
+            str(int(self.is_pyi)),
+        ]
+        return &quot;.&quot;.join(parts)
+
+
+def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -&gt; bool:
+    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)
 
 
 def read_pyproject_toml(
</pre>

</details>

<details><summary>Responsible change</summary>

<pre>@@ -3598,16 +3697,16 @@ def can_omit_invisible_parens(line: Line, line_length: int) -&gt; bool:
     return False
 
 
-def get_cache_file(line_length: int, mode: FileMode) -&gt; Path:
-    return CACHE_DIR / f&quot;cache.{line_length}.{mode.value}.pickle&quot;
+def get_cache_file(mode: FileMode) -&gt; Path:
+    return CACHE_DIR / f&quot;cache.{mode.get_cache_key()}.pickle&quot;
 
 
-def read_cache(line_length: int, mode: FileMode) -&gt; Cache:
+def read_cache(mode: FileMode) -&gt; Cache:
     &quot;&quot;&quot;Read the cache if it exists and is well formed.
 
     If it is not well formed, the call to write_cache later should resolve the issue.
     &quot;&quot;&quot;
-    cache_file = get_cache_file(line_length, mode)
+    cache_file = get_cache_file(mode)
     if not cache_file.exists():
         return {}
 
</pre>

</details>

**README.md:886-886** ([source](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/README.md#L886))

<blockquote>* Linux: &#96;/home/&lt;username&gt;/.cache/black/&lt;version&gt;/cache.&lt;line-length&gt;.&lt;file-mode&gt;.pickle&#96;</blockquote>

Character offsets: 35239–35328 (end exclusive).

Update the documented filename layout to describe the new composite key; review its fields rather than guessing runtime values.

Evidence: deterministic.

[Before code](https://github.com/psf/black/blob/a9d8af466a65b7d88ea35e0ff4c460175098260e/black.py#L3601-L3602)

[After code](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/black.py#L3700-L3701)

<details><summary>Responsible change</summary>

<pre>@@ -111,32 +112,86 @@ class Changed(Enum):
     YES = 2
 
 
-class FileMode(Flag):
-    AUTO_DETECT = 0
-    PYTHON36 = 1
-    PYI = 2
-    NO_STRING_NORMALIZATION = 4
-    NO_NUMERIC_UNDERSCORE_NORMALIZATION = 8
+class TargetVersion(Enum):
+    PYPY35 = 1
+    CPY27 = 2
+    CPY33 = 3
+    CPY34 = 4
+    CPY35 = 5
+    CPY36 = 6
+    CPY37 = 7
+    CPY38 = 8
+
+    def is_python2(self) -&gt; bool:
+        return self is TargetVersion.CPY27
+
+
+PY36_VERSIONS = {TargetVersion.CPY36, TargetVersion.CPY37, TargetVersion.CPY38}
+
+
+class Feature(Enum):
+    # All string literals are unicode
+    UNICODE_LITERALS = 1
+    F_STRINGS = 2
+    NUMERIC_UNDERSCORES = 3
+    TRAILING_COMMA = 4
+
+
+VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {
+    TargetVersion.CPY27: set(),
+    TargetVersion.PYPY35: {Feature.UNICODE_LITERALS, Feature.F_STRINGS},
+    TargetVersion.CPY33: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY34: {Feature.UNICODE_LITERALS},
+    TargetVersion.CPY35: {Feature.UNICODE_LITERALS, Feature.TRAILING_COMMA},
+    TargetVersion.CPY36: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY37: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+    TargetVersion.CPY38: {
+        Feature.UNICODE_LITERALS,
+        Feature.F_STRINGS,
+        Feature.NUMERIC_UNDERSCORES,
+        Feature.TRAILING_COMMA,
+    },
+}
 
-    @classmethod
-    def from_configuration(
-        cls,
-        *,
-        py36: bool,
-        pyi: bool,
-        skip_string_normalization: bool,
-        skip_numeric_underscore_normalization: bool,
-    ) -&gt; &quot;FileMode&quot;:
-        mode = cls.AUTO_DETECT
-        if py36:
-            mode |= cls.PYTHON36
-        if pyi:
-            mode |= cls.PYI
-        if skip_string_normalization:
-            mode |= cls.NO_STRING_NORMALIZATION
-        if skip_numeric_underscore_normalization:
-            mode |= cls.NO_NUMERIC_UNDERSCORE_NORMALIZATION
-        return mode
+
+@dataclass
+class FileMode:
+    target_versions: Set[TargetVersion] = Factory(set)
+    line_length: int = DEFAULT_LINE_LENGTH
+    numeric_underscore_normalization: bool = True
+    string_normalization: bool = True
+    is_pyi: bool = False
+
+    def get_cache_key(self) -&gt; str:
+        if self.target_versions:
+            version_str = &quot;,&quot;.join(
+                str(version.value)
+                for version in sorted(self.target_versions, key=lambda v: v.value)
+            )
+        else:
+            version_str = &quot;-&quot;
+        parts = [
+            version_str,
+            str(self.line_length),
+            str(int(self.numeric_underscore_normalization)),
+            str(int(self.string_normalization)),
+            str(int(self.is_pyi)),
+        ]
+        return &quot;.&quot;.join(parts)
+
+
+def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -&gt; bool:
+    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)
 
 
 def read_pyproject_toml(
</pre>

</details>

<details><summary>Responsible change</summary>

<pre>@@ -3598,16 +3697,16 @@ def can_omit_invisible_parens(line: Line, line_length: int) -&gt; bool:
     return False
 
 
-def get_cache_file(line_length: int, mode: FileMode) -&gt; Path:
-    return CACHE_DIR / f&quot;cache.{line_length}.{mode.value}.pickle&quot;
+def get_cache_file(mode: FileMode) -&gt; Path:
+    return CACHE_DIR / f&quot;cache.{mode.get_cache_key()}.pickle&quot;
 
 
-def read_cache(line_length: int, mode: FileMode) -&gt; Cache:
+def read_cache(mode: FileMode) -&gt; Cache:
     &quot;&quot;&quot;Read the cache if it exists and is well formed.
 
     If it is not well formed, the call to write_cache later should resolve the issue.
     &quot;&quot;&quot;
-    cache_file = get_cache_file(line_length, mode)
+    cache_file = get_cache_file(mode)
     if not cache_file.exists():
         return {}
 
</pre>

</details>

Abstentions: 0. Runtime: 8.306s.

- Warning: tests/data/expression.py: cannot use starred expression here (&lt;unknown&gt;, line 148)
- Warning: tests/data/numeric_literals_py2.py: invalid decimal literal (&lt;unknown&gt;, line 3)
- Warning: tests/data/python2.py: &#x27;u&#x27; and &#x27;r&#x27; prefixes are incompatible (&lt;unknown&gt;, line 11)
- Warning: tests/data/python2_unicode_literals.py: &#x27;u&#x27; and &#x27;r&#x27; prefixes are incompatible (&lt;unknown&gt;, line 8)

## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
