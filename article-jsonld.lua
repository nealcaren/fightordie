-- article-jsonld.lua
-- Pandoc Lua filter that emits a per-article schema.org JSON-LD block
-- and a few corrected OpenGraph article tags into the HTML head.
--
-- Reads from frontmatter:
--   title, description, date
--   author (list of name objects, or string)
--   citation.volume, citation.issue, citation.page
--   subjects, people, places, organizations, events
--
-- Skips index/listing/browse pages (anything without a citation.volume).

local stringify = pandoc.utils.stringify
local ptype = pandoc.utils.type
local json = pandoc.json

local function is_list(v)
  local t = ptype(v)
  return t == 'List' or t == 'MetaList'
end

local function is_map(v)
  -- A frontmatter map shows up as a plain Lua table without a numeric [1]
  return type(v) == 'table' and not is_list(v) and ptype(v) ~= 'Inlines' and ptype(v) ~= 'Blocks'
end

local function get_str(v)
  if v == nil then return nil end
  return stringify(v)
end

local function get_list(v)
  if v == nil then return nil end
  if not is_list(v) then return { stringify(v) } end
  local out = {}
  for _, item in ipairs(v) do
    table.insert(out, stringify(item))
  end
  return out
end

local function citation_field(meta, field)
  if meta.citation == nil then return nil end
  if not is_map(meta.citation) then return nil end
  if meta.citation[field] == nil then return nil end
  return stringify(meta.citation[field])
end

local function build_author(meta)
  local default = {
    ['@type'] = 'Person',
    name = 'W.E.B. Du Bois',
    sameAs = 'https://en.wikipedia.org/wiki/W._E._B._Du_Bois',
  }
  if meta.author == nil then return default end

  local first = meta.author
  if is_list(first) then first = first[1] end
  if first == nil then return default end

  local name
  if is_map(first) and first.name then
    if is_map(first.name) then
      local given = first.name.given and stringify(first.name.given) or ''
      local family = first.name.family and stringify(first.name.family) or ''
      name = (given .. ' ' .. family):gsub('^%s+', ''):gsub('%s+$', '')
    else
      name = stringify(first.name)
    end
  else
    name = stringify(first)
  end

  local obj = { ['@type'] = 'Person', name = name }
  if name:find('Du Bois') then
    obj.sameAs = 'https://en.wikipedia.org/wiki/W._E._B._Du_Bois'
  end
  return obj
end

local function html_escape(s)
  return (s:gsub('&', '&amp;'):gsub('<', '&lt;'):gsub('>', '&gt;'):gsub('"', '&quot;'))
end

function Meta(meta)
  local volume = citation_field(meta, 'volume')
  local issue = citation_field(meta, 'issue')
  if volume == nil or issue == nil then
    return meta
  end

  local title = get_str(meta.title) or ''
  local description = get_str(meta.description) or ''
  local date_str = get_str(meta.date) or ''
  local page = citation_field(meta, 'page')

  local author = build_author(meta)

  local about = {}
  for _, s in ipairs(get_list(meta.subjects) or {}) do
    table.insert(about, { ['@type'] = 'Thing', name = s })
  end
  for _, s in ipairs(get_list(meta.organizations) or {}) do
    table.insert(about, { ['@type'] = 'Organization', name = s })
  end
  for _, s in ipairs(get_list(meta.events) or {}) do
    table.insert(about, { ['@type'] = 'Thing', name = s })
  end

  local mentions = {}
  for _, s in ipairs(get_list(meta.people) or {}) do
    table.insert(mentions, { ['@type'] = 'Person', name = s })
  end
  for _, s in ipairs(get_list(meta.places) or {}) do
    table.insert(mentions, { ['@type'] = 'Place', name = s })
  end

  local periodical = {
    ['@type'] = 'Periodical',
    name = 'The Crisis',
    issn = '0011-1422',
    publisher = {
      ['@type'] = 'Organization',
      name = 'National Association for the Advancement of Colored People',
      sameAs = 'https://en.wikipedia.org/wiki/NAACP',
    },
    volumeNumber = volume,
    issueNumber = issue,
  }

  local article = {
    ['@context'] = 'https://schema.org',
    ['@type'] = 'Article',
    headline = title,
    description = description,
    author = author,
    datePublished = date_str,
    inLanguage = 'en',
    isAccessibleForFree = true,
    license = 'https://creativecommons.org/publicdomain/mark/1.0/',
    isPartOf = periodical,
  }
  if page then article.pagination = page end
  if #about > 0 then article.about = about end
  if #mentions > 0 then article.mentions = mentions end

  local jsonld_str = json.encode(article)

  local section = nil
  local cats = get_list(meta.categories)
  if cats and #cats > 0 then section = cats[1] end

  local lines = {}
  table.insert(lines, '<script type="application/ld+json">')
  table.insert(lines, jsonld_str)
  table.insert(lines, '</script>')
  table.insert(lines, '<meta property="og:type" content="article">')
  if date_str ~= '' then
    table.insert(lines, '<meta property="article:published_time" content="' .. html_escape(date_str) .. '">')
  end
  table.insert(lines, '<meta property="article:author" content="' .. html_escape(author.name) .. '">')
  if section then
    table.insert(lines, '<meta property="article:section" content="' .. html_escape(section) .. '">')
  end
  for _, s in ipairs(get_list(meta.subjects) or {}) do
    table.insert(lines, '<meta property="article:tag" content="' .. html_escape(s) .. '">')
  end

  local block = table.concat(lines, '\n')

  local header_includes = meta['header-includes']
  if header_includes == nil then
    header_includes = pandoc.MetaList({})
  elseif header_includes.t ~= 'MetaList' then
    header_includes = pandoc.MetaList({ header_includes })
  end
  table.insert(header_includes, pandoc.MetaBlocks({ pandoc.RawBlock('html', block) }))
  meta['header-includes'] = header_includes

  return meta
end
