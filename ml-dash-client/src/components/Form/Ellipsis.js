import React, {useEffect, useRef, useState} from 'react';
import toFinite from 'lodash.tofinite';
import measureText from 'measure-text';
import units from 'units-css';
import useDebounce from "react-use/lib/useDebounce";
import {debounce} from "throttle-debounce";

/*
A React component for truncating text in the middle of the string.

This component automatically calculates the required width and height of the text
taking into consideration any inherited font and line-height styles, and compares it to
the available space to determine whether to truncate or not.

By default the component will truncate the middle of the text if
the text would otherwise overflow using a position 0 at the start of the string,
and position 0 at the end of the string.

You can pass start and end props a number to offset this position, or alternatively
a Regular Expression to calculate these positions dynamically against the text itself.
*/
export default function Ellipsis({
                                   ellipsis = '...',
                                   end = 0,
                                   onResizeDebounce = 100,
                                   smartCopy = 'all',
                                   start = 0,
                                   style = {},
                                   text = '',
                                   padding = 0,
                                   ..._props
                                 }) {

  // Debounce the parsing of the text so that the component has had time to render its DOM for measurement calculations

  function onCopy(event) {
    // If smart copy is not enabled, simply return and use the default behaviour of the copy event
    if (!smartCopy) return;
    const selectedText = window.getSelection().toString();

    // If smartCopy is set to partial or if smartCopy is set to all and the entire string was selected
    // copy the original full text to the user's clipboard
    if (smartCopy === 'partial' || (smartCopy === 'all' && selectedText === state.truncatedText)) {
      event.preventDefault();
      const clipboardData = event.clipboardData || window.clipboardData || event.originalEvent.clipboardData;
      clipboardData.setData('text/plain', text);
    }
  }

  // parseTextForTruncation = debounce(parseTextForTruncation.bind(this), 0);
  // onResize = debounce(onResize.bind(this), onResizeDebounceMs);

  function getStartOffset(start, text) {
    if (start === '' || start === null) return 0;
    if (!isNaN(parseInt(start, 10))) return Math.round(toFinite(start));
    const result = new RegExp(start).exec(text);
    return result ? result.index + result[0].length : 0;
  }

  function getEndOffset(end, text) {
    if (end === '' || end === null) return 0;
    if (!isNaN(parseInt(end, 10))) return Math.round(toFinite(end));
    const result = new RegExp(end).exec(text);
    return result ? result[0].length : 0;
  }

  const getTextMeasurement = (node) => {
    const text = node.textContent;

    const {fontFamily, fontSize, fontWeight, fontStyle} = window.getComputedStyle(node);
    const {width, height} = measureText({text, fontFamily, fontSize, fontWeight, fontStyle, lineHeight: 1});
    return {width: width.value, height: height.value};
  };

  const getComponentMeasurement = (node, padding = 0) => {
    const {offsetWidth, offsetHeight} = node;

    return {
      // note: add padding here.
      width: units.parse(offsetWidth, 'px').value - padding,
      height: units.parse(offsetHeight, 'px').value
    };
  };

  function calculateMeasurements() {
    return {
      component: getComponentMeasurement(rootRef.current, units.convert("px", padding, rootRef.current)),
      ellipsis: getTextMeasurement(ellipsisRef.current),
      text: getTextMeasurement(textRef.current)
    };
  }

  function truncateText(measurements) {
    const {start, end} = state;

    if (Math.round(measurements.component.width) <= Math.round(measurements.ellipsis.width))
      return ellipsis;

    const delta = Math.ceil(measurements.text.width - measurements.component.width);
    const totalLettersToRemove = Math.ceil(((delta / measurements.ellipsis.width)));
    const middleIndex = Math.round(text.length / 2);

    const preserveLeftSide = text.slice(0, start);
    const leftSide = text.slice(start, middleIndex - totalLettersToRemove);
    const rightSide = text.slice(middleIndex + totalLettersToRemove, text.length - end);
    const preserveRightSide = text.slice(text.length - end, text.length);

    return `${preserveLeftSide}${leftSide}${ellipsis}${rightSide}${preserveRightSide}`;
  }

  function parseTextForTruncation(text) {
    const measurements = calculateMeasurements();

    const truncatedText =
        (Math.round(measurements.text.width) > Math.round(measurements.component.width))
            ? truncateText(measurements)
            : text;

    setState({...state, truncatedText});
  }

  const rootRef = useRef(null);
  const textRef = useRef(null);
  const ellipsisRef = useRef(null);

  const [state, setState] = useState({
    truncatedText: "",
    start: getStartOffset(start, text),
    end: getEndOffset(end, text)
  });

  useEffect(() => {
    setState({
      ...state,
      text,
      start: getStartOffset(start, text),
      end: getEndOffset(end, text)
    })
  }, [text, start, end]);

  //todo: change to `useSize` from react-use library;
  useEffect(() => {
    parseTextForTruncation(text);
    let onResize = debounce(onResizeDebounce, () => parseTextForTruncation(text));
    window.addEventListener('resize', onResize);
    // unmount here.
    return () => window.removeEventListener('resize', onResize);
  }, [text, setState]);


  const {truncatedText} = state;

  const componentStyle = {
    ...style,
    display: 'block',
    overflow: 'hidden',
    whiteSpace: 'nowrap'
  };

  const hiddenStyle = {
    display: 'none'
  };

  return (
      <div ref={rootRef} onCopy={onCopy} style={componentStyle} {..._props}>
        <span ref={textRef} style={hiddenStyle}>{text}</span>
        <span ref={ellipsisRef} style={hiddenStyle}>{ellipsis}</span>
        {truncatedText}
      </div>
  );
}
