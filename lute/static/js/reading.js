let reload_text_div = function () {
  const context = window.parent.document;
  const bookid = $("#book_id", context).val();
  const pagenum = $("#page_num", context).val();
  const url = `/read/renderpage/${bookid}/${pagenum}`;
  const repel = $("#thetext", context);

  // Force remove the old popup.
  // ref https://stackoverflow.com/questions/19266886/
  //   tooltip-not-disappearing
  $("div.ui-tooltip", context).remove();

  repel.load(url);
};
