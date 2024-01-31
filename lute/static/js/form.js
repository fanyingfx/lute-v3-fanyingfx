// The parent tag list, managed by tagify.
// Global reference needed for runtime inspection of tag list.
var parents_tagify = null;

// TODO zzfuture fix: acceptance tests for all interactions

// Monitor state of form change.
let form_changed = false;

$("form :input").change(function () {
  form_changed = true;
});

let setup_parent_tagify = function (input) {
  const tagify = new Tagify(input, {
    placeholder: "Parents",
    editTags: false,
    autoComplete: { enabled: true, rightKey: true, tabKey: true },
    enforceWhitelist: false,
    whitelist: [],
    dropdown: {
      enabled: 2, // Min 2 chars - this doesn't seem to work.
      maxItems: 15,
      mapValueTo: "suggestion", // Field to display
      placeAbove: false, // Always put the dropdown below the textbox
    },
    templates: {
      dropdownFooter(suggestions) {
        var hasMore = suggestions.length - this.settings.dropdown.maxItems;
        if (hasMore <= 0) return "";
        return `<footer data-selector='tagify-suggestions-footer' class="${this.settings.classNames.dropdownFooter}">
                (more items available, please refine your search.)</footer>`;
      },
    },
  }); // end tagify

  tagify.on("click", function (e) {
    // Exit early if language not set - will not handle, too complicated.
    const langid = document.getElementById("language_id").value;
    const clickedTagText = e.detail.data.value;
    if (langid === "0" || clickedTagText === "") {
      return;
    }

    if (form_changed) {
      const msg =
        "You have unsaved changes, going to the parent will lose them.  Continue?";
      if (!confirm(msg)) return;
    }

    let url = "";
    let eir = $("#embedded-in-frame").data("embed");
    if (eir == "True") {
      url = `/read/termform/${langid}/${clickedTagText}`;
    } else {
      url = `/term/editbytext/${langid}/${clickedTagText}`;
    }
    window.location.href = url;
  });

  tagify.on("add remove", function (e) {
    // The #parents_list text box isn't changed consistently
    // during events, so we have to check the tagify var
    // itself, which has an accurate list of current tags.
    // console.log(e);
    // console.log(e.detail);
    const single_parent = parents_tagify.value.length == 1;
    const cb = $("#sync_status");
    cb.prop("checked", single_parent);
    if (single_parent) cb.removeAttr("disabled");
    else cb.attr("disabled", true);

    // If adding a single parent, inherit its status.
    if (e.type == "add" && single_parent) {
      if (e.detail && e.detail.data && e.detail.data.status) {
        const targetValue = e.detail.data.status;
        var radioButtons = document.getElementsByName("status");
        for (var i = 0; i < radioButtons.length; i++) {
          if (radioButtons[i].value == targetValue) {
            // console.log(`found at i = ${i}`);
            radioButtons[i].checked = true;
            break;
          }
        }
      }
    }
  });

  // Autocomplete
  var controller;
  tagify.on("input", onInput);
  function onInput(e) {
    tagify.whitelist = null; // Reset whitelist.
    if (e.detail.value == "" || e.detail.value.length < 2) {
      controller && controller.abort();
      tagify.whitelist = [];
      tagify.loading(false).dropdown.hide();
      return;
    }
    const s = encodeURIComponent(e.detail.value);
    // console.log(s);
    const langid = parseInt(document.getElementById("language_id").value);

    // https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort
    controller && controller.abort();
    controller = new AbortController();

    let make_dropdown = function (hsh) {
      // console.log(`text: ${hsh.text}`);
      const txt = decodeURIComponent(hsh.text);
      let t = hsh.translation ?? "";
      if (t == "") {
        return txt;
      }
      t = t.replaceAll("\n", "; ").replaceAll("\r", "");
      const maxlen = 70;
      if (t.length > maxlen) {
        t = t.substring(0, maxlen) + "...";
      }
      return `${txt} (${t})`;
    };

    tagify.loading(true); // spinning animation during fetch.
    fetch(`/term/search/${s}/${langid}`, { signal: controller.signal })
      .then((RES) => RES.json())
      .then(function (data) {
        const newWhitelist = data.map((a) => ({
          value: a.text,
          suggestion: make_dropdown(a),
          status: a.status,
        }));
        tagify.whitelist = newWhitelist; // update whitelist Array in-place
        const sdecode = decodeURIComponent(s);
        tagify.loading(false).dropdown.show(sdecode); // render the suggestions dropdown
      })
      .catch((err) => {
        if (err.name === "AbortError") {
          // Do nothing, fetch was aborted due to another fetch.
          // console.log('AbortError: Fetch request aborted');
        } else {
          console.log(`error: ${err}`);
        }
      });
  } // end function onInput

  return tagify;
}; // end setup_parent_tagify

/** Parents are in the tagify-managed #parentslist input box. */
let get_parents = function () {
  // During form load, and in "steady state" (i.e., after the tags
  // have been added or removed, and the focus has switched to
  // another control) the #sync_status text box is loaded with the
  // values.
  const pdata = $("#parentslist").val();
  if ((pdata ?? "") == "") {
    return [];
  }
  const j = JSON.parse(pdata);
  const parents = j.map((e) => e.value);
  return parents;
};

let enable_disable_sync_status_checkbox = function () {
  const cb = $("#sync_status");
  if (get_parents().length == 1) cb.removeAttr("disabled");
  else cb.attr("disabled", true);
};

let setup_tags_tagify = function (input) {
  const tagify = new Tagify(input, {
    placeholder: "Tags",
    editTags: false,
    autoComplete: { enabled: true, rightKey: true, tabKey: true },
    enforceWhitelist: false,
    whitelist: TAGS,
  }); // end tagify
};

// TODO zzfuture fix: check term autofocus
// lute.js should send an "autofocus" flag, I believe.
let handleAutofocus = function () {
  const wordfield = $("#text");
  const transfield = $("#translation");

  if ($("#autofocus").val() != "false") {
    if (wordfield.val()) {
      transfield.focus();
    } else {
      wordfield.focus();
    }
  }
};

$(document).ready(function () {
  var parentslist = document.getElementById("parentslist");
  parents_tagify = setup_parent_tagify(parentslist);
  var termtagslist = document.getElementById("termtagslist");
  var termtags_tagify = setup_tags_tagify(termtagslist);
  var sentencetagslist = document.getElementById("snotetags");
  var sentencetags_tagify = setup_tags_tagify(sentencetagslist);
  get_note();

  if (($("#text").val() ?? "") != "") {
    do_term_lookup(false);
  }

  // Post message re form opened.
  // Note have to use this rather than the better
  // this.dispatchEvent(new Event("termFormOpened"));
  // because this form is opened in a frame.
  window.parent.postMessage({ event: "LuteTermFormOpened" }, "*");

  enable_disable_sync_status_checkbox();
});

/** LOOKUPS */

// Term lookups cycle through the available dictionaries in the language.
var termdictindex = 0;

let open_new_lookup_window = function (url) {
  window.open(
    url,
    "otherwin",
    //'width=800, height=400, scrollbars=yes, menubar=no, resizable=yes, status=no'
  );
};

let get_lookup_url = function (dicturl, term) {
  let ret = dicturl;

  // Terms are saved with zero-width space between each token;
  // remove that for dict searches!
  const zeroWidthSpace = "\u200b";
  const sqlZWS = "%E2%80%8B";
  const cleantext = term.replaceAll(zeroWidthSpace, "").replace(/\s+/g, " ");
  const searchterm = encodeURIComponent(cleantext).replaceAll(sqlZWS, "");
  ret = ret.replace("###", searchterm);
  // console.log(ret);
  return ret;
};

let do_image_lookup = function () {
  const langid = $("#language_id").val();
  const text = $("#text").val();

  if (
    langid == null ||
    langid == "" ||
    parseInt(langid) == 0 ||
    text == null ||
    text == ""
  ) {
    alert("Please select a language and enter the term.");
    return;
  }

  let use_text = text;

  // If there is a single parent, use that as the basis of the lookup.
  const parents = get_parents();
  if (parents.length == 1) use_text = parents[0];

  const raw_bing_url =
    "https://www.bing.com/images/search?q=###&form=HDRSC2&first=1&tsc=ImageHoverTitle";
  const binghash = raw_bing_url.replace(
    "https://www.bing.com/images/search?",
    "",
  );
  const url = `/bing/search/${langid}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
  top.frames.dictframe.location.href = url;
};

/**
 * Either open a new window, or show the result in the correct frame.
 */
let show_lookup_page = function (
  dicturl,
  text,
  langid,
  allow_open_new_web_page = true,
) {
  const is_bing = dicturl.indexOf("www.bing.com") != -1;
  if (is_bing) {
    let use_text = text;
    const binghash = dicturl.replace("https://www.bing.com/images/search?", "");
    const url = `/bing/search/${langid}/${encodeURIComponent(use_text)}/${encodeURIComponent(binghash)}`;
    top.frames.dictframe.location.href = url;
    return;
  }

  // TODO zzfuture fix: fix_language_dict_asterisk
  // The URL shouldn not be prepended with trash
  // (e.g. "*http://" means "open an external window", while
  // "http://" means "this can be opened in an iframe."
  // Instead, each dict should have an "is_external" property.
  const is_external = dicturl.charAt(0) == "*";
  if (is_external) {
    if (!allow_open_new_web_page) {
      console.log("Declining to open external web page.");
      return;
    }
    dicturl = dicturl.slice(1);
    const url = get_lookup_url(dicturl, text);
    open_new_lookup_window(url);
    return;
  }

  // Fallback: open in frame.
  const url = get_lookup_url(dicturl, text);
  top.frames.dictframe.location.href = url;
};

function do_term_lookup(allow_open_new_web_page = true) {
  const langid = $("#language_id").val();
  if (langid == null || langid == "" || parseInt(langid) == 0) {
    alert("Please select a language.");
    return;
  }

  const termdicts = LANGUAGES[langid].term;
  const usedict = termdicts[termdictindex];
  if ($("#lemma").val()) {
    text = $("#lemma").val();
  } else {
    text = $("#text").val();
  }
  show_lookup_page(usedict, text, langid, allow_open_new_web_page);

  termdictindex++;
  if (termdictindex >= termdicts.length) termdictindex = 0;
}

function show_term_sentences() {
  const langid = $("#language_id").val();
  const txt = $("#text").val();
  // %E2%80%8B is the zero-width string.  The term is reparsed
  // on the server, so this doesn't need to be sent.
  const t = encodeURIComponent(txt).replaceAll("%E2%80%8B", "");
  if (langid == "0" || t == "") return;
  const url = `/term/sentences/${langid}/${t}`;
  top.frames.dictframe.location.href = url;
}

function deleteTerm() {
  const msg =
    "Are you sure you want to delete this term?\n\n" +
    "This action cannot be undone, and if this term has children, they will be orphaned.";
  if (!confirm(msg)) return;
  term = $("#curr_term");
  termid = term.data("termid");
  embed_in_reading_frame = $("#embedded-in-frame").data("embed");

  $.post(`/term/delete/${termid}`, function (data) {
    if (embed_in_reading_frame === "True") {
      // If on reading page, reload page
      parent.location.reload();
    } else {
      // If on term page, go to term listing
      window.location.href = "/term/index";
    }
  });
}
function searchword() {
  const langid = $("#language_id").val();
  if (langid == null || langid == "" || parseInt(langid) == 0) {
    alert("Please select a language.");
    return;
  }

  const termdicts = LANGUAGES[langid].term;
  console.log(termdicts);
  let termdictindex = 0;
  const dicturl = termdicts[termdictindex];
  const word = document.getElementById("_searchword").value;
  const url = get_lookup_url(dicturl, word);
  top.frames.dictframe.location.href = url;
}
async function get_note() {
  const queryParams = new URLSearchParams(window.location.search);
  const bookid = queryParams.get("bookid");
  const pagenum = queryParams.get("pagenum");
  const sentence = queryParams.get("sentence");
  let url = `/read/sentencenote/${bookid}/${pagenum}/${sentence}`;
  let noteEle = document.getElementById("sentencenote");
  let stagsEle = document.getElementById("snotetags");
  let stagfy = stagsEle.__tagify;
  if (!stagfy) {
    stagfy = new Tagify(stagsEle);
  }
  let res = await fetch(url);
  let data = await res.json();
  noteEle.value = data.sentence_note;
  stagfy.addTags(data.tags);
}
async function update_note() {
  const queryParams = new URLSearchParams(window.location.search);
  const bookid = queryParams.get("bookid");
  const pagenum = queryParams.get("pagenum");
  const sentence = queryParams.get("sentence");
  const url = `/read/sentencenote/${bookid}/${pagenum}/${sentence}`;
  const stagsEle = document.getElementById("snotetags");
  let stagfy = stagsEle.__tagify;

  if (!stagfy) {
    stagfy = new Tagify(stagsEle);
  }
  const noteEle = document.getElementById("sentencenote");
  const messagefloatWindow = document.getElementById("sentence-note-message");
  const text = noteEle.value;
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=utf-8", // Specify the content type if sending JSON data
    },
    body: JSON.stringify({ new_note: text, tags: stagfy.value }), // Convert the data to JSON format
  };
  const response = await fetch(url, options);
  const data = await response.json(); // Parse the JSON response

  messagefloatWindow.style.display = "block";
  messagefloatWindow.innerText = data.message;
  if (data.status === "2") {
    stagfy.removeAllTags();
  }
  reload_text_div();
  setTimeout(() => (messagefloatWindow.style.display = "none"), 1500);
}

const searchwordbox = document.getElementById("_searchword");

// Add event listener for keypress event
searchwordbox.addEventListener("keypress", function (event) {
  // Check if the pressed key is Enter (keyCode 13)
  if (event.key === "Enter") {
    // Call a function or perform an action when Enter key is pressed
    searchword();
  }
});
