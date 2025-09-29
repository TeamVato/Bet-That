var yy = Object.defineProperty;
var Hc = (e) => {
  throw TypeError(e);
};
var vy = (e, t, n) =>
  t in e ? yy(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : (e[t] = n);
var Hs = (e, t, n) => vy(e, typeof t != 'symbol' ? t + '' : t, n),
  Ba = (e, t, n) => t.has(e) || Hc('Cannot ' + n);
var v = (e, t, n) => (Ba(e, t, 'read from private field'), n ? n.call(e) : t.get(e)),
  W = (e, t, n) =>
    t.has(e)
      ? Hc('Cannot add the same private member more than once')
      : t instanceof WeakSet
        ? t.add(e)
        : t.set(e, n),
  M = (e, t, n, r) => (Ba(e, t, 'write to private field'), r ? r.call(e, n) : t.set(e, n), n),
  ne = (e, t, n) => (Ba(e, t, 'access private method'), n);
var ll = (e, t, n, r) => ({
  set _(s) {
    M(e, t, s, n);
  },
  get _() {
    return v(e, t, r);
  },
});
function gy(e, t) {
  for (var n = 0; n < t.length; n++) {
    const r = t[n];
    if (typeof r != 'string' && !Array.isArray(r)) {
      for (const s in r)
        if (s !== 'default' && !(s in e)) {
          const i = Object.getOwnPropertyDescriptor(r, s);
          i && Object.defineProperty(e, s, i.get ? i : { enumerable: !0, get: () => r[s] });
        }
    }
  }
  return Object.freeze(Object.defineProperty(e, Symbol.toStringTag, { value: 'Module' }));
}
(function () {
  const t = document.createElement('link').relList;
  if (t && t.supports && t.supports('modulepreload')) return;
  for (const s of document.querySelectorAll('link[rel="modulepreload"]')) r(s);
  new MutationObserver((s) => {
    for (const i of s)
      if (i.type === 'childList')
        for (const l of i.addedNodes) l.tagName === 'LINK' && l.rel === 'modulepreload' && r(l);
  }).observe(document, { childList: !0, subtree: !0 });
  function n(s) {
    const i = {};
    return (
      s.integrity && (i.integrity = s.integrity),
      s.referrerPolicy && (i.referrerPolicy = s.referrerPolicy),
      s.crossOrigin === 'use-credentials'
        ? (i.credentials = 'include')
        : s.crossOrigin === 'anonymous'
          ? (i.credentials = 'omit')
          : (i.credentials = 'same-origin'),
      i
    );
  }
  function r(s) {
    if (s.ep) return;
    s.ep = !0;
    const i = n(s);
    fetch(s.href, i);
  }
})();
function xy(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, 'default') ? e.default : e;
}
var ch = { exports: {} },
  wa = {},
  dh = { exports: {} },
  se = {};
/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var qi = Symbol.for('react.element'),
  wy = Symbol.for('react.portal'),
  _y = Symbol.for('react.fragment'),
  ky = Symbol.for('react.strict_mode'),
  Sy = Symbol.for('react.profiler'),
  Cy = Symbol.for('react.provider'),
  Ey = Symbol.for('react.context'),
  Ny = Symbol.for('react.forward_ref'),
  jy = Symbol.for('react.suspense'),
  Ry = Symbol.for('react.memo'),
  Ty = Symbol.for('react.lazy'),
  Kc = Symbol.iterator;
function Oy(e) {
  return e === null || typeof e != 'object'
    ? null
    : ((e = (Kc && e[Kc]) || e['@@iterator']), typeof e == 'function' ? e : null);
}
var fh = {
    isMounted: function () {
      return !1;
    },
    enqueueForceUpdate: function () {},
    enqueueReplaceState: function () {},
    enqueueSetState: function () {},
  },
  hh = Object.assign,
  ph = {};
function Vs(e, t, n) {
  ((this.props = e), (this.context = t), (this.refs = ph), (this.updater = n || fh));
}
Vs.prototype.isReactComponent = {};
Vs.prototype.setState = function (e, t) {
  if (typeof e != 'object' && typeof e != 'function' && e != null)
    throw Error(
      'setState(...): takes an object of state variables to update or a function which returns an object of state variables.',
    );
  this.updater.enqueueSetState(this, e, t, 'setState');
};
Vs.prototype.forceUpdate = function (e) {
  this.updater.enqueueForceUpdate(this, e, 'forceUpdate');
};
function mh() {}
mh.prototype = Vs.prototype;
function zu(e, t, n) {
  ((this.props = e), (this.context = t), (this.refs = ph), (this.updater = n || fh));
}
var Uu = (zu.prototype = new mh());
Uu.constructor = zu;
hh(Uu, Vs.prototype);
Uu.isPureReactComponent = !0;
var qc = Array.isArray,
  yh = Object.prototype.hasOwnProperty,
  Vu = { current: null },
  vh = { key: !0, ref: !0, __self: !0, __source: !0 };
function gh(e, t, n) {
  var r,
    s = {},
    i = null,
    l = null;
  if (t != null)
    for (r in (t.ref !== void 0 && (l = t.ref), t.key !== void 0 && (i = '' + t.key), t))
      yh.call(t, r) && !vh.hasOwnProperty(r) && (s[r] = t[r]);
  var a = arguments.length - 2;
  if (a === 1) s.children = n;
  else if (1 < a) {
    for (var o = Array(a), u = 0; u < a; u++) o[u] = arguments[u + 2];
    s.children = o;
  }
  if (e && e.defaultProps) for (r in ((a = e.defaultProps), a)) s[r] === void 0 && (s[r] = a[r]);
  return { $$typeof: qi, type: e, key: i, ref: l, props: s, _owner: Vu.current };
}
function Py(e, t) {
  return { $$typeof: qi, type: e.type, key: t, ref: e.ref, props: e.props, _owner: e._owner };
}
function $u(e) {
  return typeof e == 'object' && e !== null && e.$$typeof === qi;
}
function by(e) {
  var t = { '=': '=0', ':': '=2' };
  return (
    '$' +
    e.replace(/[=:]/g, function (n) {
      return t[n];
    })
  );
}
var Gc = /\/+/g;
function Qa(e, t) {
  return typeof e == 'object' && e !== null && e.key != null ? by('' + e.key) : t.toString(36);
}
function Nl(e, t, n, r, s) {
  var i = typeof e;
  (i === 'undefined' || i === 'boolean') && (e = null);
  var l = !1;
  if (e === null) l = !0;
  else
    switch (i) {
      case 'string':
      case 'number':
        l = !0;
        break;
      case 'object':
        switch (e.$$typeof) {
          case qi:
          case wy:
            l = !0;
        }
    }
  if (l)
    return (
      (l = e),
      (s = s(l)),
      (e = r === '' ? '.' + Qa(l, 0) : r),
      qc(s)
        ? ((n = ''),
          e != null && (n = e.replace(Gc, '$&/') + '/'),
          Nl(s, t, n, '', function (u) {
            return u;
          }))
        : s != null &&
          ($u(s) &&
            (s = Py(
              s,
              n +
                (!s.key || (l && l.key === s.key) ? '' : ('' + s.key).replace(Gc, '$&/') + '/') +
                e,
            )),
          t.push(s)),
      1
    );
  if (((l = 0), (r = r === '' ? '.' : r + ':'), qc(e)))
    for (var a = 0; a < e.length; a++) {
      i = e[a];
      var o = r + Qa(i, a);
      l += Nl(i, t, n, o, s);
    }
  else if (((o = Oy(e)), typeof o == 'function'))
    for (e = o.call(e), a = 0; !(i = e.next()).done; )
      ((i = i.value), (o = r + Qa(i, a++)), (l += Nl(i, t, n, o, s)));
  else if (i === 'object')
    throw (
      (t = String(e)),
      Error(
        'Objects are not valid as a React child (found: ' +
          (t === '[object Object]' ? 'object with keys {' + Object.keys(e).join(', ') + '}' : t) +
          '). If you meant to render a collection of children, use an array instead.',
      )
    );
  return l;
}
function al(e, t, n) {
  if (e == null) return e;
  var r = [],
    s = 0;
  return (
    Nl(e, r, '', '', function (i) {
      return t.call(n, i, s++);
    }),
    r
  );
}
function Ay(e) {
  if (e._status === -1) {
    var t = e._result;
    ((t = t()),
      t.then(
        function (n) {
          (e._status === 0 || e._status === -1) && ((e._status = 1), (e._result = n));
        },
        function (n) {
          (e._status === 0 || e._status === -1) && ((e._status = 2), (e._result = n));
        },
      ),
      e._status === -1 && ((e._status = 0), (e._result = t)));
  }
  if (e._status === 1) return e._result.default;
  throw e._result;
}
var at = { current: null },
  jl = { transition: null },
  Ly = { ReactCurrentDispatcher: at, ReactCurrentBatchConfig: jl, ReactCurrentOwner: Vu };
function xh() {
  throw Error('act(...) is not supported in production builds of React.');
}
se.Children = {
  map: al,
  forEach: function (e, t, n) {
    al(
      e,
      function () {
        t.apply(this, arguments);
      },
      n,
    );
  },
  count: function (e) {
    var t = 0;
    return (
      al(e, function () {
        t++;
      }),
      t
    );
  },
  toArray: function (e) {
    return (
      al(e, function (t) {
        return t;
      }) || []
    );
  },
  only: function (e) {
    if (!$u(e))
      throw Error('React.Children.only expected to receive a single React element child.');
    return e;
  },
};
se.Component = Vs;
se.Fragment = _y;
se.Profiler = Sy;
se.PureComponent = zu;
se.StrictMode = ky;
se.Suspense = jy;
se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = Ly;
se.act = xh;
se.cloneElement = function (e, t, n) {
  if (e == null)
    throw Error(
      'React.cloneElement(...): The argument must be a React element, but you passed ' + e + '.',
    );
  var r = hh({}, e.props),
    s = e.key,
    i = e.ref,
    l = e._owner;
  if (t != null) {
    if (
      (t.ref !== void 0 && ((i = t.ref), (l = Vu.current)),
      t.key !== void 0 && (s = '' + t.key),
      e.type && e.type.defaultProps)
    )
      var a = e.type.defaultProps;
    for (o in t)
      yh.call(t, o) &&
        !vh.hasOwnProperty(o) &&
        (r[o] = t[o] === void 0 && a !== void 0 ? a[o] : t[o]);
  }
  var o = arguments.length - 2;
  if (o === 1) r.children = n;
  else if (1 < o) {
    a = Array(o);
    for (var u = 0; u < o; u++) a[u] = arguments[u + 2];
    r.children = a;
  }
  return { $$typeof: qi, type: e.type, key: s, ref: i, props: r, _owner: l };
};
se.createContext = function (e) {
  return (
    (e = {
      $$typeof: Ey,
      _currentValue: e,
      _currentValue2: e,
      _threadCount: 0,
      Provider: null,
      Consumer: null,
      _defaultValue: null,
      _globalName: null,
    }),
    (e.Provider = { $$typeof: Cy, _context: e }),
    (e.Consumer = e)
  );
};
se.createElement = gh;
se.createFactory = function (e) {
  var t = gh.bind(null, e);
  return ((t.type = e), t);
};
se.createRef = function () {
  return { current: null };
};
se.forwardRef = function (e) {
  return { $$typeof: Ny, render: e };
};
se.isValidElement = $u;
se.lazy = function (e) {
  return { $$typeof: Ty, _payload: { _status: -1, _result: e }, _init: Ay };
};
se.memo = function (e, t) {
  return { $$typeof: Ry, type: e, compare: t === void 0 ? null : t };
};
se.startTransition = function (e) {
  var t = jl.transition;
  jl.transition = {};
  try {
    e();
  } finally {
    jl.transition = t;
  }
};
se.unstable_act = xh;
se.useCallback = function (e, t) {
  return at.current.useCallback(e, t);
};
se.useContext = function (e) {
  return at.current.useContext(e);
};
se.useDebugValue = function () {};
se.useDeferredValue = function (e) {
  return at.current.useDeferredValue(e);
};
se.useEffect = function (e, t) {
  return at.current.useEffect(e, t);
};
se.useId = function () {
  return at.current.useId();
};
se.useImperativeHandle = function (e, t, n) {
  return at.current.useImperativeHandle(e, t, n);
};
se.useInsertionEffect = function (e, t) {
  return at.current.useInsertionEffect(e, t);
};
se.useLayoutEffect = function (e, t) {
  return at.current.useLayoutEffect(e, t);
};
se.useMemo = function (e, t) {
  return at.current.useMemo(e, t);
};
se.useReducer = function (e, t, n) {
  return at.current.useReducer(e, t, n);
};
se.useRef = function (e) {
  return at.current.useRef(e);
};
se.useState = function (e) {
  return at.current.useState(e);
};
se.useSyncExternalStore = function (e, t, n) {
  return at.current.useSyncExternalStore(e, t, n);
};
se.useTransition = function () {
  return at.current.useTransition();
};
se.version = '18.3.1';
dh.exports = se;
var E = dh.exports;
const Xe = xy(E),
  Fy = gy({ __proto__: null, default: Xe }, [E]);
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var Iy = E,
  My = Symbol.for('react.element'),
  Dy = Symbol.for('react.fragment'),
  zy = Object.prototype.hasOwnProperty,
  Uy = Iy.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,
  Vy = { key: !0, ref: !0, __self: !0, __source: !0 };
function wh(e, t, n) {
  var r,
    s = {},
    i = null,
    l = null;
  (n !== void 0 && (i = '' + n),
    t.key !== void 0 && (i = '' + t.key),
    t.ref !== void 0 && (l = t.ref));
  for (r in t) zy.call(t, r) && !Vy.hasOwnProperty(r) && (s[r] = t[r]);
  if (e && e.defaultProps) for (r in ((t = e.defaultProps), t)) s[r] === void 0 && (s[r] = t[r]);
  return { $$typeof: My, type: e, key: i, ref: l, props: s, _owner: Uy.current };
}
wa.Fragment = Dy;
wa.jsx = wh;
wa.jsxs = wh;
ch.exports = wa;
var c = ch.exports,
  wo = {},
  _h = { exports: {} },
  St = {},
  kh = { exports: {} },
  Sh = {};
/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ (function (e) {
  function t(D, K) {
    var Y = D.length;
    D.push(K);
    e: for (; 0 < Y; ) {
      var ge = (Y - 1) >>> 1,
        Re = D[ge];
      if (0 < s(Re, K)) ((D[ge] = K), (D[Y] = Re), (Y = ge));
      else break e;
    }
  }
  function n(D) {
    return D.length === 0 ? null : D[0];
  }
  function r(D) {
    if (D.length === 0) return null;
    var K = D[0],
      Y = D.pop();
    if (Y !== K) {
      D[0] = Y;
      e: for (var ge = 0, Re = D.length, an = Re >>> 1; ge < an; ) {
        var Et = 2 * (ge + 1) - 1,
          on = D[Et],
          It = Et + 1,
          Kt = D[It];
        if (0 > s(on, Y))
          It < Re && 0 > s(Kt, on)
            ? ((D[ge] = Kt), (D[It] = Y), (ge = It))
            : ((D[ge] = on), (D[Et] = Y), (ge = Et));
        else if (It < Re && 0 > s(Kt, Y)) ((D[ge] = Kt), (D[It] = Y), (ge = It));
        else break e;
      }
    }
    return K;
  }
  function s(D, K) {
    var Y = D.sortIndex - K.sortIndex;
    return Y !== 0 ? Y : D.id - K.id;
  }
  if (typeof performance == 'object' && typeof performance.now == 'function') {
    var i = performance;
    e.unstable_now = function () {
      return i.now();
    };
  } else {
    var l = Date,
      a = l.now();
    e.unstable_now = function () {
      return l.now() - a;
    };
  }
  var o = [],
    u = [],
    f = 1,
    h = null,
    p = 3,
    k = !1,
    S = !1,
    _ = !1,
    N = typeof setTimeout == 'function' ? setTimeout : null,
    y = typeof clearTimeout == 'function' ? clearTimeout : null,
    d = typeof setImmediate < 'u' ? setImmediate : null;
  typeof navigator < 'u' &&
    navigator.scheduling !== void 0 &&
    navigator.scheduling.isInputPending !== void 0 &&
    navigator.scheduling.isInputPending.bind(navigator.scheduling);
  function m(D) {
    for (var K = n(u); K !== null; ) {
      if (K.callback === null) r(u);
      else if (K.startTime <= D) (r(u), (K.sortIndex = K.expirationTime), t(o, K));
      else break;
      K = n(u);
    }
  }
  function x(D) {
    if (((_ = !1), m(D), !S))
      if (n(o) !== null) ((S = !0), ie(j));
      else {
        var K = n(u);
        K !== null && qe(x, K.startTime - D);
      }
  }
  function j(D, K) {
    ((S = !1), _ && ((_ = !1), y(L), (L = -1)), (k = !0));
    var Y = p;
    try {
      for (m(K), h = n(o); h !== null && (!(h.expirationTime > K) || (D && !H())); ) {
        var ge = h.callback;
        if (typeof ge == 'function') {
          ((h.callback = null), (p = h.priorityLevel));
          var Re = ge(h.expirationTime <= K);
          ((K = e.unstable_now()),
            typeof Re == 'function' ? (h.callback = Re) : h === n(o) && r(o),
            m(K));
        } else r(o);
        h = n(o);
      }
      if (h !== null) var an = !0;
      else {
        var Et = n(u);
        (Et !== null && qe(x, Et.startTime - K), (an = !1));
      }
      return an;
    } finally {
      ((h = null), (p = Y), (k = !1));
    }
  }
  var O = !1,
    A = null,
    L = -1,
    q = 5,
    P = -1;
  function H() {
    return !(e.unstable_now() - P < q);
  }
  function G() {
    if (A !== null) {
      var D = e.unstable_now();
      P = D;
      var K = !0;
      try {
        K = A(!0, D);
      } finally {
        K ? ee() : ((O = !1), (A = null));
      }
    } else O = !1;
  }
  var ee;
  if (typeof d == 'function')
    ee = function () {
      d(G);
    };
  else if (typeof MessageChannel < 'u') {
    var ve = new MessageChannel(),
      ae = ve.port2;
    ((ve.port1.onmessage = G),
      (ee = function () {
        ae.postMessage(null);
      }));
  } else
    ee = function () {
      N(G, 0);
    };
  function ie(D) {
    ((A = D), O || ((O = !0), ee()));
  }
  function qe(D, K) {
    L = N(function () {
      D(e.unstable_now());
    }, K);
  }
  ((e.unstable_IdlePriority = 5),
    (e.unstable_ImmediatePriority = 1),
    (e.unstable_LowPriority = 4),
    (e.unstable_NormalPriority = 3),
    (e.unstable_Profiling = null),
    (e.unstable_UserBlockingPriority = 2),
    (e.unstable_cancelCallback = function (D) {
      D.callback = null;
    }),
    (e.unstable_continueExecution = function () {
      S || k || ((S = !0), ie(j));
    }),
    (e.unstable_forceFrameRate = function (D) {
      0 > D || 125 < D
        ? console.error(
            'forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported',
          )
        : (q = 0 < D ? Math.floor(1e3 / D) : 5);
    }),
    (e.unstable_getCurrentPriorityLevel = function () {
      return p;
    }),
    (e.unstable_getFirstCallbackNode = function () {
      return n(o);
    }),
    (e.unstable_next = function (D) {
      switch (p) {
        case 1:
        case 2:
        case 3:
          var K = 3;
          break;
        default:
          K = p;
      }
      var Y = p;
      p = K;
      try {
        return D();
      } finally {
        p = Y;
      }
    }),
    (e.unstable_pauseExecution = function () {}),
    (e.unstable_requestPaint = function () {}),
    (e.unstable_runWithPriority = function (D, K) {
      switch (D) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
          break;
        default:
          D = 3;
      }
      var Y = p;
      p = D;
      try {
        return K();
      } finally {
        p = Y;
      }
    }),
    (e.unstable_scheduleCallback = function (D, K, Y) {
      var ge = e.unstable_now();
      switch (
        (typeof Y == 'object' && Y !== null
          ? ((Y = Y.delay), (Y = typeof Y == 'number' && 0 < Y ? ge + Y : ge))
          : (Y = ge),
        D)
      ) {
        case 1:
          var Re = -1;
          break;
        case 2:
          Re = 250;
          break;
        case 5:
          Re = 1073741823;
          break;
        case 4:
          Re = 1e4;
          break;
        default:
          Re = 5e3;
      }
      return (
        (Re = Y + Re),
        (D = {
          id: f++,
          callback: K,
          priorityLevel: D,
          startTime: Y,
          expirationTime: Re,
          sortIndex: -1,
        }),
        Y > ge
          ? ((D.sortIndex = Y),
            t(u, D),
            n(o) === null && D === n(u) && (_ ? (y(L), (L = -1)) : (_ = !0), qe(x, Y - ge)))
          : ((D.sortIndex = Re), t(o, D), S || k || ((S = !0), ie(j))),
        D
      );
    }),
    (e.unstable_shouldYield = H),
    (e.unstable_wrapCallback = function (D) {
      var K = p;
      return function () {
        var Y = p;
        p = K;
        try {
          return D.apply(this, arguments);
        } finally {
          p = Y;
        }
      };
    }));
})(Sh);
kh.exports = Sh;
var $y = kh.exports;
/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var By = E,
  _t = $y;
function R(e) {
  for (
    var t = 'https://reactjs.org/docs/error-decoder.html?invariant=' + e, n = 1;
    n < arguments.length;
    n++
  )
    t += '&args[]=' + encodeURIComponent(arguments[n]);
  return (
    'Minified React error #' +
    e +
    '; visit ' +
    t +
    ' for the full message or use the non-minified dev environment for full errors and additional helpful warnings.'
  );
}
var Ch = new Set(),
  ki = {};
function Br(e, t) {
  (Rs(e, t), Rs(e + 'Capture', t));
}
function Rs(e, t) {
  for (ki[e] = t, e = 0; e < t.length; e++) Ch.add(t[e]);
}
var _n = !(
    typeof window > 'u' ||
    typeof window.document > 'u' ||
    typeof window.document.createElement > 'u'
  ),
  _o = Object.prototype.hasOwnProperty,
  Qy =
    /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,
  Yc = {},
  Xc = {};
function Wy(e) {
  return _o.call(Xc, e) ? !0 : _o.call(Yc, e) ? !1 : Qy.test(e) ? (Xc[e] = !0) : ((Yc[e] = !0), !1);
}
function Zy(e, t, n, r) {
  if (n !== null && n.type === 0) return !1;
  switch (typeof t) {
    case 'function':
    case 'symbol':
      return !0;
    case 'boolean':
      return r
        ? !1
        : n !== null
          ? !n.acceptsBooleans
          : ((e = e.toLowerCase().slice(0, 5)), e !== 'data-' && e !== 'aria-');
    default:
      return !1;
  }
}
function Hy(e, t, n, r) {
  if (t === null || typeof t > 'u' || Zy(e, t, n, r)) return !0;
  if (r) return !1;
  if (n !== null)
    switch (n.type) {
      case 3:
        return !t;
      case 4:
        return t === !1;
      case 5:
        return isNaN(t);
      case 6:
        return isNaN(t) || 1 > t;
    }
  return !1;
}
function ot(e, t, n, r, s, i, l) {
  ((this.acceptsBooleans = t === 2 || t === 3 || t === 4),
    (this.attributeName = r),
    (this.attributeNamespace = s),
    (this.mustUseProperty = n),
    (this.propertyName = e),
    (this.type = t),
    (this.sanitizeURL = i),
    (this.removeEmptyString = l));
}
var Ke = {};
'children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style'
  .split(' ')
  .forEach(function (e) {
    Ke[e] = new ot(e, 0, !1, e, null, !1, !1);
  });
[
  ['acceptCharset', 'accept-charset'],
  ['className', 'class'],
  ['htmlFor', 'for'],
  ['httpEquiv', 'http-equiv'],
].forEach(function (e) {
  var t = e[0];
  Ke[t] = new ot(t, 1, !1, e[1], null, !1, !1);
});
['contentEditable', 'draggable', 'spellCheck', 'value'].forEach(function (e) {
  Ke[e] = new ot(e, 2, !1, e.toLowerCase(), null, !1, !1);
});
['autoReverse', 'externalResourcesRequired', 'focusable', 'preserveAlpha'].forEach(function (e) {
  Ke[e] = new ot(e, 2, !1, e, null, !1, !1);
});
'allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope'
  .split(' ')
  .forEach(function (e) {
    Ke[e] = new ot(e, 3, !1, e.toLowerCase(), null, !1, !1);
  });
['checked', 'multiple', 'muted', 'selected'].forEach(function (e) {
  Ke[e] = new ot(e, 3, !0, e, null, !1, !1);
});
['capture', 'download'].forEach(function (e) {
  Ke[e] = new ot(e, 4, !1, e, null, !1, !1);
});
['cols', 'rows', 'size', 'span'].forEach(function (e) {
  Ke[e] = new ot(e, 6, !1, e, null, !1, !1);
});
['rowSpan', 'start'].forEach(function (e) {
  Ke[e] = new ot(e, 5, !1, e.toLowerCase(), null, !1, !1);
});
var Bu = /[\-:]([a-z])/g;
function Qu(e) {
  return e[1].toUpperCase();
}
'accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height'
  .split(' ')
  .forEach(function (e) {
    var t = e.replace(Bu, Qu);
    Ke[t] = new ot(t, 1, !1, e, null, !1, !1);
  });
'xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type'
  .split(' ')
  .forEach(function (e) {
    var t = e.replace(Bu, Qu);
    Ke[t] = new ot(t, 1, !1, e, 'http://www.w3.org/1999/xlink', !1, !1);
  });
['xml:base', 'xml:lang', 'xml:space'].forEach(function (e) {
  var t = e.replace(Bu, Qu);
  Ke[t] = new ot(t, 1, !1, e, 'http://www.w3.org/XML/1998/namespace', !1, !1);
});
['tabIndex', 'crossOrigin'].forEach(function (e) {
  Ke[e] = new ot(e, 1, !1, e.toLowerCase(), null, !1, !1);
});
Ke.xlinkHref = new ot('xlinkHref', 1, !1, 'xlink:href', 'http://www.w3.org/1999/xlink', !0, !1);
['src', 'href', 'action', 'formAction'].forEach(function (e) {
  Ke[e] = new ot(e, 1, !1, e.toLowerCase(), null, !0, !0);
});
function Wu(e, t, n, r) {
  var s = Ke.hasOwnProperty(t) ? Ke[t] : null;
  (s !== null
    ? s.type !== 0
    : r || !(2 < t.length) || (t[0] !== 'o' && t[0] !== 'O') || (t[1] !== 'n' && t[1] !== 'N')) &&
    (Hy(t, n, s, r) && (n = null),
    r || s === null
      ? Wy(t) && (n === null ? e.removeAttribute(t) : e.setAttribute(t, '' + n))
      : s.mustUseProperty
        ? (e[s.propertyName] = n === null ? (s.type === 3 ? !1 : '') : n)
        : ((t = s.attributeName),
          (r = s.attributeNamespace),
          n === null
            ? e.removeAttribute(t)
            : ((s = s.type),
              (n = s === 3 || (s === 4 && n === !0) ? '' : '' + n),
              r ? e.setAttributeNS(r, t, n) : e.setAttribute(t, n))));
}
var Nn = By.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,
  ol = Symbol.for('react.element'),
  Xr = Symbol.for('react.portal'),
  Jr = Symbol.for('react.fragment'),
  Zu = Symbol.for('react.strict_mode'),
  ko = Symbol.for('react.profiler'),
  Eh = Symbol.for('react.provider'),
  Nh = Symbol.for('react.context'),
  Hu = Symbol.for('react.forward_ref'),
  So = Symbol.for('react.suspense'),
  Co = Symbol.for('react.suspense_list'),
  Ku = Symbol.for('react.memo'),
  bn = Symbol.for('react.lazy'),
  jh = Symbol.for('react.offscreen'),
  Jc = Symbol.iterator;
function Ks(e) {
  return e === null || typeof e != 'object'
    ? null
    : ((e = (Jc && e[Jc]) || e['@@iterator']), typeof e == 'function' ? e : null);
}
var je = Object.assign,
  Wa;
function si(e) {
  if (Wa === void 0)
    try {
      throw Error();
    } catch (n) {
      var t = n.stack.trim().match(/\n( *(at )?)/);
      Wa = (t && t[1]) || '';
    }
  return (
    `
` +
    Wa +
    e
  );
}
var Za = !1;
function Ha(e, t) {
  if (!e || Za) return '';
  Za = !0;
  var n = Error.prepareStackTrace;
  Error.prepareStackTrace = void 0;
  try {
    if (t)
      if (
        ((t = function () {
          throw Error();
        }),
        Object.defineProperty(t.prototype, 'props', {
          set: function () {
            throw Error();
          },
        }),
        typeof Reflect == 'object' && Reflect.construct)
      ) {
        try {
          Reflect.construct(t, []);
        } catch (u) {
          var r = u;
        }
        Reflect.construct(e, [], t);
      } else {
        try {
          t.call();
        } catch (u) {
          r = u;
        }
        e.call(t.prototype);
      }
    else {
      try {
        throw Error();
      } catch (u) {
        r = u;
      }
      e();
    }
  } catch (u) {
    if (u && r && typeof u.stack == 'string') {
      for (
        var s = u.stack.split(`
`),
          i = r.stack.split(`
`),
          l = s.length - 1,
          a = i.length - 1;
        1 <= l && 0 <= a && s[l] !== i[a];

      )
        a--;
      for (; 1 <= l && 0 <= a; l--, a--)
        if (s[l] !== i[a]) {
          if (l !== 1 || a !== 1)
            do
              if ((l--, a--, 0 > a || s[l] !== i[a])) {
                var o =
                  `
` + s[l].replace(' at new ', ' at ');
                return (
                  e.displayName &&
                    o.includes('<anonymous>') &&
                    (o = o.replace('<anonymous>', e.displayName)),
                  o
                );
              }
            while (1 <= l && 0 <= a);
          break;
        }
    }
  } finally {
    ((Za = !1), (Error.prepareStackTrace = n));
  }
  return (e = e ? e.displayName || e.name : '') ? si(e) : '';
}
function Ky(e) {
  switch (e.tag) {
    case 5:
      return si(e.type);
    case 16:
      return si('Lazy');
    case 13:
      return si('Suspense');
    case 19:
      return si('SuspenseList');
    case 0:
    case 2:
    case 15:
      return ((e = Ha(e.type, !1)), e);
    case 11:
      return ((e = Ha(e.type.render, !1)), e);
    case 1:
      return ((e = Ha(e.type, !0)), e);
    default:
      return '';
  }
}
function Eo(e) {
  if (e == null) return null;
  if (typeof e == 'function') return e.displayName || e.name || null;
  if (typeof e == 'string') return e;
  switch (e) {
    case Jr:
      return 'Fragment';
    case Xr:
      return 'Portal';
    case ko:
      return 'Profiler';
    case Zu:
      return 'StrictMode';
    case So:
      return 'Suspense';
    case Co:
      return 'SuspenseList';
  }
  if (typeof e == 'object')
    switch (e.$$typeof) {
      case Nh:
        return (e.displayName || 'Context') + '.Consumer';
      case Eh:
        return (e._context.displayName || 'Context') + '.Provider';
      case Hu:
        var t = e.render;
        return (
          (e = e.displayName),
          e ||
            ((e = t.displayName || t.name || ''),
            (e = e !== '' ? 'ForwardRef(' + e + ')' : 'ForwardRef')),
          e
        );
      case Ku:
        return ((t = e.displayName || null), t !== null ? t : Eo(e.type) || 'Memo');
      case bn:
        ((t = e._payload), (e = e._init));
        try {
          return Eo(e(t));
        } catch {}
    }
  return null;
}
function qy(e) {
  var t = e.type;
  switch (e.tag) {
    case 24:
      return 'Cache';
    case 9:
      return (t.displayName || 'Context') + '.Consumer';
    case 10:
      return (t._context.displayName || 'Context') + '.Provider';
    case 18:
      return 'DehydratedFragment';
    case 11:
      return (
        (e = t.render),
        (e = e.displayName || e.name || ''),
        t.displayName || (e !== '' ? 'ForwardRef(' + e + ')' : 'ForwardRef')
      );
    case 7:
      return 'Fragment';
    case 5:
      return t;
    case 4:
      return 'Portal';
    case 3:
      return 'Root';
    case 6:
      return 'Text';
    case 16:
      return Eo(t);
    case 8:
      return t === Zu ? 'StrictMode' : 'Mode';
    case 22:
      return 'Offscreen';
    case 12:
      return 'Profiler';
    case 21:
      return 'Scope';
    case 13:
      return 'Suspense';
    case 19:
      return 'SuspenseList';
    case 25:
      return 'TracingMarker';
    case 1:
    case 0:
    case 17:
    case 2:
    case 14:
    case 15:
      if (typeof t == 'function') return t.displayName || t.name || null;
      if (typeof t == 'string') return t;
  }
  return null;
}
function or(e) {
  switch (typeof e) {
    case 'boolean':
    case 'number':
    case 'string':
    case 'undefined':
      return e;
    case 'object':
      return e;
    default:
      return '';
  }
}
function Rh(e) {
  var t = e.type;
  return (e = e.nodeName) && e.toLowerCase() === 'input' && (t === 'checkbox' || t === 'radio');
}
function Gy(e) {
  var t = Rh(e) ? 'checked' : 'value',
    n = Object.getOwnPropertyDescriptor(e.constructor.prototype, t),
    r = '' + e[t];
  if (
    !e.hasOwnProperty(t) &&
    typeof n < 'u' &&
    typeof n.get == 'function' &&
    typeof n.set == 'function'
  ) {
    var s = n.get,
      i = n.set;
    return (
      Object.defineProperty(e, t, {
        configurable: !0,
        get: function () {
          return s.call(this);
        },
        set: function (l) {
          ((r = '' + l), i.call(this, l));
        },
      }),
      Object.defineProperty(e, t, { enumerable: n.enumerable }),
      {
        getValue: function () {
          return r;
        },
        setValue: function (l) {
          r = '' + l;
        },
        stopTracking: function () {
          ((e._valueTracker = null), delete e[t]);
        },
      }
    );
  }
}
function ul(e) {
  e._valueTracker || (e._valueTracker = Gy(e));
}
function Th(e) {
  if (!e) return !1;
  var t = e._valueTracker;
  if (!t) return !0;
  var n = t.getValue(),
    r = '';
  return (
    e && (r = Rh(e) ? (e.checked ? 'true' : 'false') : e.value),
    (e = r),
    e !== n ? (t.setValue(e), !0) : !1
  );
}
function zl(e) {
  if (((e = e || (typeof document < 'u' ? document : void 0)), typeof e > 'u')) return null;
  try {
    return e.activeElement || e.body;
  } catch {
    return e.body;
  }
}
function No(e, t) {
  var n = t.checked;
  return je({}, t, {
    defaultChecked: void 0,
    defaultValue: void 0,
    value: void 0,
    checked: n ?? e._wrapperState.initialChecked,
  });
}
function ed(e, t) {
  var n = t.defaultValue == null ? '' : t.defaultValue,
    r = t.checked != null ? t.checked : t.defaultChecked;
  ((n = or(t.value != null ? t.value : n)),
    (e._wrapperState = {
      initialChecked: r,
      initialValue: n,
      controlled: t.type === 'checkbox' || t.type === 'radio' ? t.checked != null : t.value != null,
    }));
}
function Oh(e, t) {
  ((t = t.checked), t != null && Wu(e, 'checked', t, !1));
}
function jo(e, t) {
  Oh(e, t);
  var n = or(t.value),
    r = t.type;
  if (n != null)
    r === 'number'
      ? ((n === 0 && e.value === '') || e.value != n) && (e.value = '' + n)
      : e.value !== '' + n && (e.value = '' + n);
  else if (r === 'submit' || r === 'reset') {
    e.removeAttribute('value');
    return;
  }
  (t.hasOwnProperty('value')
    ? Ro(e, t.type, n)
    : t.hasOwnProperty('defaultValue') && Ro(e, t.type, or(t.defaultValue)),
    t.checked == null && t.defaultChecked != null && (e.defaultChecked = !!t.defaultChecked));
}
function td(e, t, n) {
  if (t.hasOwnProperty('value') || t.hasOwnProperty('defaultValue')) {
    var r = t.type;
    if (!((r !== 'submit' && r !== 'reset') || (t.value !== void 0 && t.value !== null))) return;
    ((t = '' + e._wrapperState.initialValue),
      n || t === e.value || (e.value = t),
      (e.defaultValue = t));
  }
  ((n = e.name),
    n !== '' && (e.name = ''),
    (e.defaultChecked = !!e._wrapperState.initialChecked),
    n !== '' && (e.name = n));
}
function Ro(e, t, n) {
  (t !== 'number' || zl(e.ownerDocument) !== e) &&
    (n == null
      ? (e.defaultValue = '' + e._wrapperState.initialValue)
      : e.defaultValue !== '' + n && (e.defaultValue = '' + n));
}
var ii = Array.isArray;
function cs(e, t, n, r) {
  if (((e = e.options), t)) {
    t = {};
    for (var s = 0; s < n.length; s++) t['$' + n[s]] = !0;
    for (n = 0; n < e.length; n++)
      ((s = t.hasOwnProperty('$' + e[n].value)),
        e[n].selected !== s && (e[n].selected = s),
        s && r && (e[n].defaultSelected = !0));
  } else {
    for (n = '' + or(n), t = null, s = 0; s < e.length; s++) {
      if (e[s].value === n) {
        ((e[s].selected = !0), r && (e[s].defaultSelected = !0));
        return;
      }
      t !== null || e[s].disabled || (t = e[s]);
    }
    t !== null && (t.selected = !0);
  }
}
function To(e, t) {
  if (t.dangerouslySetInnerHTML != null) throw Error(R(91));
  return je({}, t, {
    value: void 0,
    defaultValue: void 0,
    children: '' + e._wrapperState.initialValue,
  });
}
function nd(e, t) {
  var n = t.value;
  if (n == null) {
    if (((n = t.children), (t = t.defaultValue), n != null)) {
      if (t != null) throw Error(R(92));
      if (ii(n)) {
        if (1 < n.length) throw Error(R(93));
        n = n[0];
      }
      t = n;
    }
    (t == null && (t = ''), (n = t));
  }
  e._wrapperState = { initialValue: or(n) };
}
function Ph(e, t) {
  var n = or(t.value),
    r = or(t.defaultValue);
  (n != null &&
    ((n = '' + n),
    n !== e.value && (e.value = n),
    t.defaultValue == null && e.defaultValue !== n && (e.defaultValue = n)),
    r != null && (e.defaultValue = '' + r));
}
function rd(e) {
  var t = e.textContent;
  t === e._wrapperState.initialValue && t !== '' && t !== null && (e.value = t);
}
function bh(e) {
  switch (e) {
    case 'svg':
      return 'http://www.w3.org/2000/svg';
    case 'math':
      return 'http://www.w3.org/1998/Math/MathML';
    default:
      return 'http://www.w3.org/1999/xhtml';
  }
}
function Oo(e, t) {
  return e == null || e === 'http://www.w3.org/1999/xhtml'
    ? bh(t)
    : e === 'http://www.w3.org/2000/svg' && t === 'foreignObject'
      ? 'http://www.w3.org/1999/xhtml'
      : e;
}
var cl,
  Ah = (function (e) {
    return typeof MSApp < 'u' && MSApp.execUnsafeLocalFunction
      ? function (t, n, r, s) {
          MSApp.execUnsafeLocalFunction(function () {
            return e(t, n, r, s);
          });
        }
      : e;
  })(function (e, t) {
    if (e.namespaceURI !== 'http://www.w3.org/2000/svg' || 'innerHTML' in e) e.innerHTML = t;
    else {
      for (
        cl = cl || document.createElement('div'),
          cl.innerHTML = '<svg>' + t.valueOf().toString() + '</svg>',
          t = cl.firstChild;
        e.firstChild;

      )
        e.removeChild(e.firstChild);
      for (; t.firstChild; ) e.appendChild(t.firstChild);
    }
  });
function Si(e, t) {
  if (t) {
    var n = e.firstChild;
    if (n && n === e.lastChild && n.nodeType === 3) {
      n.nodeValue = t;
      return;
    }
  }
  e.textContent = t;
}
var di = {
    animationIterationCount: !0,
    aspectRatio: !0,
    borderImageOutset: !0,
    borderImageSlice: !0,
    borderImageWidth: !0,
    boxFlex: !0,
    boxFlexGroup: !0,
    boxOrdinalGroup: !0,
    columnCount: !0,
    columns: !0,
    flex: !0,
    flexGrow: !0,
    flexPositive: !0,
    flexShrink: !0,
    flexNegative: !0,
    flexOrder: !0,
    gridArea: !0,
    gridRow: !0,
    gridRowEnd: !0,
    gridRowSpan: !0,
    gridRowStart: !0,
    gridColumn: !0,
    gridColumnEnd: !0,
    gridColumnSpan: !0,
    gridColumnStart: !0,
    fontWeight: !0,
    lineClamp: !0,
    lineHeight: !0,
    opacity: !0,
    order: !0,
    orphans: !0,
    tabSize: !0,
    widows: !0,
    zIndex: !0,
    zoom: !0,
    fillOpacity: !0,
    floodOpacity: !0,
    stopOpacity: !0,
    strokeDasharray: !0,
    strokeDashoffset: !0,
    strokeMiterlimit: !0,
    strokeOpacity: !0,
    strokeWidth: !0,
  },
  Yy = ['Webkit', 'ms', 'Moz', 'O'];
Object.keys(di).forEach(function (e) {
  Yy.forEach(function (t) {
    ((t = t + e.charAt(0).toUpperCase() + e.substring(1)), (di[t] = di[e]));
  });
});
function Lh(e, t, n) {
  return t == null || typeof t == 'boolean' || t === ''
    ? ''
    : n || typeof t != 'number' || t === 0 || (di.hasOwnProperty(e) && di[e])
      ? ('' + t).trim()
      : t + 'px';
}
function Fh(e, t) {
  e = e.style;
  for (var n in t)
    if (t.hasOwnProperty(n)) {
      var r = n.indexOf('--') === 0,
        s = Lh(n, t[n], r);
      (n === 'float' && (n = 'cssFloat'), r ? e.setProperty(n, s) : (e[n] = s));
    }
}
var Xy = je(
  { menuitem: !0 },
  {
    area: !0,
    base: !0,
    br: !0,
    col: !0,
    embed: !0,
    hr: !0,
    img: !0,
    input: !0,
    keygen: !0,
    link: !0,
    meta: !0,
    param: !0,
    source: !0,
    track: !0,
    wbr: !0,
  },
);
function Po(e, t) {
  if (t) {
    if (Xy[e] && (t.children != null || t.dangerouslySetInnerHTML != null)) throw Error(R(137, e));
    if (t.dangerouslySetInnerHTML != null) {
      if (t.children != null) throw Error(R(60));
      if (typeof t.dangerouslySetInnerHTML != 'object' || !('__html' in t.dangerouslySetInnerHTML))
        throw Error(R(61));
    }
    if (t.style != null && typeof t.style != 'object') throw Error(R(62));
  }
}
function bo(e, t) {
  if (e.indexOf('-') === -1) return typeof t.is == 'string';
  switch (e) {
    case 'annotation-xml':
    case 'color-profile':
    case 'font-face':
    case 'font-face-src':
    case 'font-face-uri':
    case 'font-face-format':
    case 'font-face-name':
    case 'missing-glyph':
      return !1;
    default:
      return !0;
  }
}
var Ao = null;
function qu(e) {
  return (
    (e = e.target || e.srcElement || window),
    e.correspondingUseElement && (e = e.correspondingUseElement),
    e.nodeType === 3 ? e.parentNode : e
  );
}
var Lo = null,
  ds = null,
  fs = null;
function sd(e) {
  if ((e = Xi(e))) {
    if (typeof Lo != 'function') throw Error(R(280));
    var t = e.stateNode;
    t && ((t = Ea(t)), Lo(e.stateNode, e.type, t));
  }
}
function Ih(e) {
  ds ? (fs ? fs.push(e) : (fs = [e])) : (ds = e);
}
function Mh() {
  if (ds) {
    var e = ds,
      t = fs;
    if (((fs = ds = null), sd(e), t)) for (e = 0; e < t.length; e++) sd(t[e]);
  }
}
function Dh(e, t) {
  return e(t);
}
function zh() {}
var Ka = !1;
function Uh(e, t, n) {
  if (Ka) return e(t, n);
  Ka = !0;
  try {
    return Dh(e, t, n);
  } finally {
    ((Ka = !1), (ds !== null || fs !== null) && (zh(), Mh()));
  }
}
function Ci(e, t) {
  var n = e.stateNode;
  if (n === null) return null;
  var r = Ea(n);
  if (r === null) return null;
  n = r[t];
  e: switch (t) {
    case 'onClick':
    case 'onClickCapture':
    case 'onDoubleClick':
    case 'onDoubleClickCapture':
    case 'onMouseDown':
    case 'onMouseDownCapture':
    case 'onMouseMove':
    case 'onMouseMoveCapture':
    case 'onMouseUp':
    case 'onMouseUpCapture':
    case 'onMouseEnter':
      ((r = !r.disabled) ||
        ((e = e.type),
        (r = !(e === 'button' || e === 'input' || e === 'select' || e === 'textarea'))),
        (e = !r));
      break e;
    default:
      e = !1;
  }
  if (e) return null;
  if (n && typeof n != 'function') throw Error(R(231, t, typeof n));
  return n;
}
var Fo = !1;
if (_n)
  try {
    var qs = {};
    (Object.defineProperty(qs, 'passive', {
      get: function () {
        Fo = !0;
      },
    }),
      window.addEventListener('test', qs, qs),
      window.removeEventListener('test', qs, qs));
  } catch {
    Fo = !1;
  }
function Jy(e, t, n, r, s, i, l, a, o) {
  var u = Array.prototype.slice.call(arguments, 3);
  try {
    t.apply(n, u);
  } catch (f) {
    this.onError(f);
  }
}
var fi = !1,
  Ul = null,
  Vl = !1,
  Io = null,
  ev = {
    onError: function (e) {
      ((fi = !0), (Ul = e));
    },
  };
function tv(e, t, n, r, s, i, l, a, o) {
  ((fi = !1), (Ul = null), Jy.apply(ev, arguments));
}
function nv(e, t, n, r, s, i, l, a, o) {
  if ((tv.apply(this, arguments), fi)) {
    if (fi) {
      var u = Ul;
      ((fi = !1), (Ul = null));
    } else throw Error(R(198));
    Vl || ((Vl = !0), (Io = u));
  }
}
function Qr(e) {
  var t = e,
    n = e;
  if (e.alternate) for (; t.return; ) t = t.return;
  else {
    e = t;
    do ((t = e), t.flags & 4098 && (n = t.return), (e = t.return));
    while (e);
  }
  return t.tag === 3 ? n : null;
}
function Vh(e) {
  if (e.tag === 13) {
    var t = e.memoizedState;
    if ((t === null && ((e = e.alternate), e !== null && (t = e.memoizedState)), t !== null))
      return t.dehydrated;
  }
  return null;
}
function id(e) {
  if (Qr(e) !== e) throw Error(R(188));
}
function rv(e) {
  var t = e.alternate;
  if (!t) {
    if (((t = Qr(e)), t === null)) throw Error(R(188));
    return t !== e ? null : e;
  }
  for (var n = e, r = t; ; ) {
    var s = n.return;
    if (s === null) break;
    var i = s.alternate;
    if (i === null) {
      if (((r = s.return), r !== null)) {
        n = r;
        continue;
      }
      break;
    }
    if (s.child === i.child) {
      for (i = s.child; i; ) {
        if (i === n) return (id(s), e);
        if (i === r) return (id(s), t);
        i = i.sibling;
      }
      throw Error(R(188));
    }
    if (n.return !== r.return) ((n = s), (r = i));
    else {
      for (var l = !1, a = s.child; a; ) {
        if (a === n) {
          ((l = !0), (n = s), (r = i));
          break;
        }
        if (a === r) {
          ((l = !0), (r = s), (n = i));
          break;
        }
        a = a.sibling;
      }
      if (!l) {
        for (a = i.child; a; ) {
          if (a === n) {
            ((l = !0), (n = i), (r = s));
            break;
          }
          if (a === r) {
            ((l = !0), (r = i), (n = s));
            break;
          }
          a = a.sibling;
        }
        if (!l) throw Error(R(189));
      }
    }
    if (n.alternate !== r) throw Error(R(190));
  }
  if (n.tag !== 3) throw Error(R(188));
  return n.stateNode.current === n ? e : t;
}
function $h(e) {
  return ((e = rv(e)), e !== null ? Bh(e) : null);
}
function Bh(e) {
  if (e.tag === 5 || e.tag === 6) return e;
  for (e = e.child; e !== null; ) {
    var t = Bh(e);
    if (t !== null) return t;
    e = e.sibling;
  }
  return null;
}
var Qh = _t.unstable_scheduleCallback,
  ld = _t.unstable_cancelCallback,
  sv = _t.unstable_shouldYield,
  iv = _t.unstable_requestPaint,
  be = _t.unstable_now,
  lv = _t.unstable_getCurrentPriorityLevel,
  Gu = _t.unstable_ImmediatePriority,
  Wh = _t.unstable_UserBlockingPriority,
  $l = _t.unstable_NormalPriority,
  av = _t.unstable_LowPriority,
  Zh = _t.unstable_IdlePriority,
  _a = null,
  rn = null;
function ov(e) {
  if (rn && typeof rn.onCommitFiberRoot == 'function')
    try {
      rn.onCommitFiberRoot(_a, e, void 0, (e.current.flags & 128) === 128);
    } catch {}
}
var Wt = Math.clz32 ? Math.clz32 : dv,
  uv = Math.log,
  cv = Math.LN2;
function dv(e) {
  return ((e >>>= 0), e === 0 ? 32 : (31 - ((uv(e) / cv) | 0)) | 0);
}
var dl = 64,
  fl = 4194304;
function li(e) {
  switch (e & -e) {
    case 1:
      return 1;
    case 2:
      return 2;
    case 4:
      return 4;
    case 8:
      return 8;
    case 16:
      return 16;
    case 32:
      return 32;
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return e & 4194240;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return e & 130023424;
    case 134217728:
      return 134217728;
    case 268435456:
      return 268435456;
    case 536870912:
      return 536870912;
    case 1073741824:
      return 1073741824;
    default:
      return e;
  }
}
function Bl(e, t) {
  var n = e.pendingLanes;
  if (n === 0) return 0;
  var r = 0,
    s = e.suspendedLanes,
    i = e.pingedLanes,
    l = n & 268435455;
  if (l !== 0) {
    var a = l & ~s;
    a !== 0 ? (r = li(a)) : ((i &= l), i !== 0 && (r = li(i)));
  } else ((l = n & ~s), l !== 0 ? (r = li(l)) : i !== 0 && (r = li(i)));
  if (r === 0) return 0;
  if (
    t !== 0 &&
    t !== r &&
    !(t & s) &&
    ((s = r & -r), (i = t & -t), s >= i || (s === 16 && (i & 4194240) !== 0))
  )
    return t;
  if ((r & 4 && (r |= n & 16), (t = e.entangledLanes), t !== 0))
    for (e = e.entanglements, t &= r; 0 < t; )
      ((n = 31 - Wt(t)), (s = 1 << n), (r |= e[n]), (t &= ~s));
  return r;
}
function fv(e, t) {
  switch (e) {
    case 1:
    case 2:
    case 4:
      return t + 250;
    case 8:
    case 16:
    case 32:
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return t + 5e3;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return -1;
    case 134217728:
    case 268435456:
    case 536870912:
    case 1073741824:
      return -1;
    default:
      return -1;
  }
}
function hv(e, t) {
  for (
    var n = e.suspendedLanes, r = e.pingedLanes, s = e.expirationTimes, i = e.pendingLanes;
    0 < i;

  ) {
    var l = 31 - Wt(i),
      a = 1 << l,
      o = s[l];
    (o === -1 ? (!(a & n) || a & r) && (s[l] = fv(a, t)) : o <= t && (e.expiredLanes |= a),
      (i &= ~a));
  }
}
function Mo(e) {
  return ((e = e.pendingLanes & -1073741825), e !== 0 ? e : e & 1073741824 ? 1073741824 : 0);
}
function Hh() {
  var e = dl;
  return ((dl <<= 1), !(dl & 4194240) && (dl = 64), e);
}
function qa(e) {
  for (var t = [], n = 0; 31 > n; n++) t.push(e);
  return t;
}
function Gi(e, t, n) {
  ((e.pendingLanes |= t),
    t !== 536870912 && ((e.suspendedLanes = 0), (e.pingedLanes = 0)),
    (e = e.eventTimes),
    (t = 31 - Wt(t)),
    (e[t] = n));
}
function pv(e, t) {
  var n = e.pendingLanes & ~t;
  ((e.pendingLanes = t),
    (e.suspendedLanes = 0),
    (e.pingedLanes = 0),
    (e.expiredLanes &= t),
    (e.mutableReadLanes &= t),
    (e.entangledLanes &= t),
    (t = e.entanglements));
  var r = e.eventTimes;
  for (e = e.expirationTimes; 0 < n; ) {
    var s = 31 - Wt(n),
      i = 1 << s;
    ((t[s] = 0), (r[s] = -1), (e[s] = -1), (n &= ~i));
  }
}
function Yu(e, t) {
  var n = (e.entangledLanes |= t);
  for (e = e.entanglements; n; ) {
    var r = 31 - Wt(n),
      s = 1 << r;
    ((s & t) | (e[r] & t) && (e[r] |= t), (n &= ~s));
  }
}
var pe = 0;
function Kh(e) {
  return ((e &= -e), 1 < e ? (4 < e ? (e & 268435455 ? 16 : 536870912) : 4) : 1);
}
var qh,
  Xu,
  Gh,
  Yh,
  Xh,
  Do = !1,
  hl = [],
  Yn = null,
  Xn = null,
  Jn = null,
  Ei = new Map(),
  Ni = new Map(),
  Fn = [],
  mv =
    'mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit'.split(
      ' ',
    );
function ad(e, t) {
  switch (e) {
    case 'focusin':
    case 'focusout':
      Yn = null;
      break;
    case 'dragenter':
    case 'dragleave':
      Xn = null;
      break;
    case 'mouseover':
    case 'mouseout':
      Jn = null;
      break;
    case 'pointerover':
    case 'pointerout':
      Ei.delete(t.pointerId);
      break;
    case 'gotpointercapture':
    case 'lostpointercapture':
      Ni.delete(t.pointerId);
  }
}
function Gs(e, t, n, r, s, i) {
  return e === null || e.nativeEvent !== i
    ? ((e = {
        blockedOn: t,
        domEventName: n,
        eventSystemFlags: r,
        nativeEvent: i,
        targetContainers: [s],
      }),
      t !== null && ((t = Xi(t)), t !== null && Xu(t)),
      e)
    : ((e.eventSystemFlags |= r),
      (t = e.targetContainers),
      s !== null && t.indexOf(s) === -1 && t.push(s),
      e);
}
function yv(e, t, n, r, s) {
  switch (t) {
    case 'focusin':
      return ((Yn = Gs(Yn, e, t, n, r, s)), !0);
    case 'dragenter':
      return ((Xn = Gs(Xn, e, t, n, r, s)), !0);
    case 'mouseover':
      return ((Jn = Gs(Jn, e, t, n, r, s)), !0);
    case 'pointerover':
      var i = s.pointerId;
      return (Ei.set(i, Gs(Ei.get(i) || null, e, t, n, r, s)), !0);
    case 'gotpointercapture':
      return ((i = s.pointerId), Ni.set(i, Gs(Ni.get(i) || null, e, t, n, r, s)), !0);
  }
  return !1;
}
function Jh(e) {
  var t = xr(e.target);
  if (t !== null) {
    var n = Qr(t);
    if (n !== null) {
      if (((t = n.tag), t === 13)) {
        if (((t = Vh(n)), t !== null)) {
          ((e.blockedOn = t),
            Xh(e.priority, function () {
              Gh(n);
            }));
          return;
        }
      } else if (t === 3 && n.stateNode.current.memoizedState.isDehydrated) {
        e.blockedOn = n.tag === 3 ? n.stateNode.containerInfo : null;
        return;
      }
    }
  }
  e.blockedOn = null;
}
function Rl(e) {
  if (e.blockedOn !== null) return !1;
  for (var t = e.targetContainers; 0 < t.length; ) {
    var n = zo(e.domEventName, e.eventSystemFlags, t[0], e.nativeEvent);
    if (n === null) {
      n = e.nativeEvent;
      var r = new n.constructor(n.type, n);
      ((Ao = r), n.target.dispatchEvent(r), (Ao = null));
    } else return ((t = Xi(n)), t !== null && Xu(t), (e.blockedOn = n), !1);
    t.shift();
  }
  return !0;
}
function od(e, t, n) {
  Rl(e) && n.delete(t);
}
function vv() {
  ((Do = !1),
    Yn !== null && Rl(Yn) && (Yn = null),
    Xn !== null && Rl(Xn) && (Xn = null),
    Jn !== null && Rl(Jn) && (Jn = null),
    Ei.forEach(od),
    Ni.forEach(od));
}
function Ys(e, t) {
  e.blockedOn === t &&
    ((e.blockedOn = null),
    Do || ((Do = !0), _t.unstable_scheduleCallback(_t.unstable_NormalPriority, vv)));
}
function ji(e) {
  function t(s) {
    return Ys(s, e);
  }
  if (0 < hl.length) {
    Ys(hl[0], e);
    for (var n = 1; n < hl.length; n++) {
      var r = hl[n];
      r.blockedOn === e && (r.blockedOn = null);
    }
  }
  for (
    Yn !== null && Ys(Yn, e),
      Xn !== null && Ys(Xn, e),
      Jn !== null && Ys(Jn, e),
      Ei.forEach(t),
      Ni.forEach(t),
      n = 0;
    n < Fn.length;
    n++
  )
    ((r = Fn[n]), r.blockedOn === e && (r.blockedOn = null));
  for (; 0 < Fn.length && ((n = Fn[0]), n.blockedOn === null); )
    (Jh(n), n.blockedOn === null && Fn.shift());
}
var hs = Nn.ReactCurrentBatchConfig,
  Ql = !0;
function gv(e, t, n, r) {
  var s = pe,
    i = hs.transition;
  hs.transition = null;
  try {
    ((pe = 1), Ju(e, t, n, r));
  } finally {
    ((pe = s), (hs.transition = i));
  }
}
function xv(e, t, n, r) {
  var s = pe,
    i = hs.transition;
  hs.transition = null;
  try {
    ((pe = 4), Ju(e, t, n, r));
  } finally {
    ((pe = s), (hs.transition = i));
  }
}
function Ju(e, t, n, r) {
  if (Ql) {
    var s = zo(e, t, n, r);
    if (s === null) (io(e, t, r, Wl, n), ad(e, r));
    else if (yv(s, e, t, n, r)) r.stopPropagation();
    else if ((ad(e, r), t & 4 && -1 < mv.indexOf(e))) {
      for (; s !== null; ) {
        var i = Xi(s);
        if ((i !== null && qh(i), (i = zo(e, t, n, r)), i === null && io(e, t, r, Wl, n), i === s))
          break;
        s = i;
      }
      s !== null && r.stopPropagation();
    } else io(e, t, r, null, n);
  }
}
var Wl = null;
function zo(e, t, n, r) {
  if (((Wl = null), (e = qu(r)), (e = xr(e)), e !== null))
    if (((t = Qr(e)), t === null)) e = null;
    else if (((n = t.tag), n === 13)) {
      if (((e = Vh(t)), e !== null)) return e;
      e = null;
    } else if (n === 3) {
      if (t.stateNode.current.memoizedState.isDehydrated)
        return t.tag === 3 ? t.stateNode.containerInfo : null;
      e = null;
    } else t !== e && (e = null);
  return ((Wl = e), null);
}
function ep(e) {
  switch (e) {
    case 'cancel':
    case 'click':
    case 'close':
    case 'contextmenu':
    case 'copy':
    case 'cut':
    case 'auxclick':
    case 'dblclick':
    case 'dragend':
    case 'dragstart':
    case 'drop':
    case 'focusin':
    case 'focusout':
    case 'input':
    case 'invalid':
    case 'keydown':
    case 'keypress':
    case 'keyup':
    case 'mousedown':
    case 'mouseup':
    case 'paste':
    case 'pause':
    case 'play':
    case 'pointercancel':
    case 'pointerdown':
    case 'pointerup':
    case 'ratechange':
    case 'reset':
    case 'resize':
    case 'seeked':
    case 'submit':
    case 'touchcancel':
    case 'touchend':
    case 'touchstart':
    case 'volumechange':
    case 'change':
    case 'selectionchange':
    case 'textInput':
    case 'compositionstart':
    case 'compositionend':
    case 'compositionupdate':
    case 'beforeblur':
    case 'afterblur':
    case 'beforeinput':
    case 'blur':
    case 'fullscreenchange':
    case 'focus':
    case 'hashchange':
    case 'popstate':
    case 'select':
    case 'selectstart':
      return 1;
    case 'drag':
    case 'dragenter':
    case 'dragexit':
    case 'dragleave':
    case 'dragover':
    case 'mousemove':
    case 'mouseout':
    case 'mouseover':
    case 'pointermove':
    case 'pointerout':
    case 'pointerover':
    case 'scroll':
    case 'toggle':
    case 'touchmove':
    case 'wheel':
    case 'mouseenter':
    case 'mouseleave':
    case 'pointerenter':
    case 'pointerleave':
      return 4;
    case 'message':
      switch (lv()) {
        case Gu:
          return 1;
        case Wh:
          return 4;
        case $l:
        case av:
          return 16;
        case Zh:
          return 536870912;
        default:
          return 16;
      }
    default:
      return 16;
  }
}
var Hn = null,
  ec = null,
  Tl = null;
function tp() {
  if (Tl) return Tl;
  var e,
    t = ec,
    n = t.length,
    r,
    s = 'value' in Hn ? Hn.value : Hn.textContent,
    i = s.length;
  for (e = 0; e < n && t[e] === s[e]; e++);
  var l = n - e;
  for (r = 1; r <= l && t[n - r] === s[i - r]; r++);
  return (Tl = s.slice(e, 1 < r ? 1 - r : void 0));
}
function Ol(e) {
  var t = e.keyCode;
  return (
    'charCode' in e ? ((e = e.charCode), e === 0 && t === 13 && (e = 13)) : (e = t),
    e === 10 && (e = 13),
    32 <= e || e === 13 ? e : 0
  );
}
function pl() {
  return !0;
}
function ud() {
  return !1;
}
function Ct(e) {
  function t(n, r, s, i, l) {
    ((this._reactName = n),
      (this._targetInst = s),
      (this.type = r),
      (this.nativeEvent = i),
      (this.target = l),
      (this.currentTarget = null));
    for (var a in e) e.hasOwnProperty(a) && ((n = e[a]), (this[a] = n ? n(i) : i[a]));
    return (
      (this.isDefaultPrevented = (
        i.defaultPrevented != null ? i.defaultPrevented : i.returnValue === !1
      )
        ? pl
        : ud),
      (this.isPropagationStopped = ud),
      this
    );
  }
  return (
    je(t.prototype, {
      preventDefault: function () {
        this.defaultPrevented = !0;
        var n = this.nativeEvent;
        n &&
          (n.preventDefault
            ? n.preventDefault()
            : typeof n.returnValue != 'unknown' && (n.returnValue = !1),
          (this.isDefaultPrevented = pl));
      },
      stopPropagation: function () {
        var n = this.nativeEvent;
        n &&
          (n.stopPropagation
            ? n.stopPropagation()
            : typeof n.cancelBubble != 'unknown' && (n.cancelBubble = !0),
          (this.isPropagationStopped = pl));
      },
      persist: function () {},
      isPersistent: pl,
    }),
    t
  );
}
var $s = {
    eventPhase: 0,
    bubbles: 0,
    cancelable: 0,
    timeStamp: function (e) {
      return e.timeStamp || Date.now();
    },
    defaultPrevented: 0,
    isTrusted: 0,
  },
  tc = Ct($s),
  Yi = je({}, $s, { view: 0, detail: 0 }),
  wv = Ct(Yi),
  Ga,
  Ya,
  Xs,
  ka = je({}, Yi, {
    screenX: 0,
    screenY: 0,
    clientX: 0,
    clientY: 0,
    pageX: 0,
    pageY: 0,
    ctrlKey: 0,
    shiftKey: 0,
    altKey: 0,
    metaKey: 0,
    getModifierState: nc,
    button: 0,
    buttons: 0,
    relatedTarget: function (e) {
      return e.relatedTarget === void 0
        ? e.fromElement === e.srcElement
          ? e.toElement
          : e.fromElement
        : e.relatedTarget;
    },
    movementX: function (e) {
      return 'movementX' in e
        ? e.movementX
        : (e !== Xs &&
            (Xs && e.type === 'mousemove'
              ? ((Ga = e.screenX - Xs.screenX), (Ya = e.screenY - Xs.screenY))
              : (Ya = Ga = 0),
            (Xs = e)),
          Ga);
    },
    movementY: function (e) {
      return 'movementY' in e ? e.movementY : Ya;
    },
  }),
  cd = Ct(ka),
  _v = je({}, ka, { dataTransfer: 0 }),
  kv = Ct(_v),
  Sv = je({}, Yi, { relatedTarget: 0 }),
  Xa = Ct(Sv),
  Cv = je({}, $s, { animationName: 0, elapsedTime: 0, pseudoElement: 0 }),
  Ev = Ct(Cv),
  Nv = je({}, $s, {
    clipboardData: function (e) {
      return 'clipboardData' in e ? e.clipboardData : window.clipboardData;
    },
  }),
  jv = Ct(Nv),
  Rv = je({}, $s, { data: 0 }),
  dd = Ct(Rv),
  Tv = {
    Esc: 'Escape',
    Spacebar: ' ',
    Left: 'ArrowLeft',
    Up: 'ArrowUp',
    Right: 'ArrowRight',
    Down: 'ArrowDown',
    Del: 'Delete',
    Win: 'OS',
    Menu: 'ContextMenu',
    Apps: 'ContextMenu',
    Scroll: 'ScrollLock',
    MozPrintableKey: 'Unidentified',
  },
  Ov = {
    8: 'Backspace',
    9: 'Tab',
    12: 'Clear',
    13: 'Enter',
    16: 'Shift',
    17: 'Control',
    18: 'Alt',
    19: 'Pause',
    20: 'CapsLock',
    27: 'Escape',
    32: ' ',
    33: 'PageUp',
    34: 'PageDown',
    35: 'End',
    36: 'Home',
    37: 'ArrowLeft',
    38: 'ArrowUp',
    39: 'ArrowRight',
    40: 'ArrowDown',
    45: 'Insert',
    46: 'Delete',
    112: 'F1',
    113: 'F2',
    114: 'F3',
    115: 'F4',
    116: 'F5',
    117: 'F6',
    118: 'F7',
    119: 'F8',
    120: 'F9',
    121: 'F10',
    122: 'F11',
    123: 'F12',
    144: 'NumLock',
    145: 'ScrollLock',
    224: 'Meta',
  },
  Pv = { Alt: 'altKey', Control: 'ctrlKey', Meta: 'metaKey', Shift: 'shiftKey' };
function bv(e) {
  var t = this.nativeEvent;
  return t.getModifierState ? t.getModifierState(e) : (e = Pv[e]) ? !!t[e] : !1;
}
function nc() {
  return bv;
}
var Av = je({}, Yi, {
    key: function (e) {
      if (e.key) {
        var t = Tv[e.key] || e.key;
        if (t !== 'Unidentified') return t;
      }
      return e.type === 'keypress'
        ? ((e = Ol(e)), e === 13 ? 'Enter' : String.fromCharCode(e))
        : e.type === 'keydown' || e.type === 'keyup'
          ? Ov[e.keyCode] || 'Unidentified'
          : '';
    },
    code: 0,
    location: 0,
    ctrlKey: 0,
    shiftKey: 0,
    altKey: 0,
    metaKey: 0,
    repeat: 0,
    locale: 0,
    getModifierState: nc,
    charCode: function (e) {
      return e.type === 'keypress' ? Ol(e) : 0;
    },
    keyCode: function (e) {
      return e.type === 'keydown' || e.type === 'keyup' ? e.keyCode : 0;
    },
    which: function (e) {
      return e.type === 'keypress'
        ? Ol(e)
        : e.type === 'keydown' || e.type === 'keyup'
          ? e.keyCode
          : 0;
    },
  }),
  Lv = Ct(Av),
  Fv = je({}, ka, {
    pointerId: 0,
    width: 0,
    height: 0,
    pressure: 0,
    tangentialPressure: 0,
    tiltX: 0,
    tiltY: 0,
    twist: 0,
    pointerType: 0,
    isPrimary: 0,
  }),
  fd = Ct(Fv),
  Iv = je({}, Yi, {
    touches: 0,
    targetTouches: 0,
    changedTouches: 0,
    altKey: 0,
    metaKey: 0,
    ctrlKey: 0,
    shiftKey: 0,
    getModifierState: nc,
  }),
  Mv = Ct(Iv),
  Dv = je({}, $s, { propertyName: 0, elapsedTime: 0, pseudoElement: 0 }),
  zv = Ct(Dv),
  Uv = je({}, ka, {
    deltaX: function (e) {
      return 'deltaX' in e ? e.deltaX : 'wheelDeltaX' in e ? -e.wheelDeltaX : 0;
    },
    deltaY: function (e) {
      return 'deltaY' in e
        ? e.deltaY
        : 'wheelDeltaY' in e
          ? -e.wheelDeltaY
          : 'wheelDelta' in e
            ? -e.wheelDelta
            : 0;
    },
    deltaZ: 0,
    deltaMode: 0,
  }),
  Vv = Ct(Uv),
  $v = [9, 13, 27, 32],
  rc = _n && 'CompositionEvent' in window,
  hi = null;
_n && 'documentMode' in document && (hi = document.documentMode);
var Bv = _n && 'TextEvent' in window && !hi,
  np = _n && (!rc || (hi && 8 < hi && 11 >= hi)),
  hd = ' ',
  pd = !1;
function rp(e, t) {
  switch (e) {
    case 'keyup':
      return $v.indexOf(t.keyCode) !== -1;
    case 'keydown':
      return t.keyCode !== 229;
    case 'keypress':
    case 'mousedown':
    case 'focusout':
      return !0;
    default:
      return !1;
  }
}
function sp(e) {
  return ((e = e.detail), typeof e == 'object' && 'data' in e ? e.data : null);
}
var es = !1;
function Qv(e, t) {
  switch (e) {
    case 'compositionend':
      return sp(t);
    case 'keypress':
      return t.which !== 32 ? null : ((pd = !0), hd);
    case 'textInput':
      return ((e = t.data), e === hd && pd ? null : e);
    default:
      return null;
  }
}
function Wv(e, t) {
  if (es)
    return e === 'compositionend' || (!rc && rp(e, t))
      ? ((e = tp()), (Tl = ec = Hn = null), (es = !1), e)
      : null;
  switch (e) {
    case 'paste':
      return null;
    case 'keypress':
      if (!(t.ctrlKey || t.altKey || t.metaKey) || (t.ctrlKey && t.altKey)) {
        if (t.char && 1 < t.char.length) return t.char;
        if (t.which) return String.fromCharCode(t.which);
      }
      return null;
    case 'compositionend':
      return np && t.locale !== 'ko' ? null : t.data;
    default:
      return null;
  }
}
var Zv = {
  color: !0,
  date: !0,
  datetime: !0,
  'datetime-local': !0,
  email: !0,
  month: !0,
  number: !0,
  password: !0,
  range: !0,
  search: !0,
  tel: !0,
  text: !0,
  time: !0,
  url: !0,
  week: !0,
};
function md(e) {
  var t = e && e.nodeName && e.nodeName.toLowerCase();
  return t === 'input' ? !!Zv[e.type] : t === 'textarea';
}
function ip(e, t, n, r) {
  (Ih(r),
    (t = Zl(t, 'onChange')),
    0 < t.length &&
      ((n = new tc('onChange', 'change', null, n, r)), e.push({ event: n, listeners: t })));
}
var pi = null,
  Ri = null;
function Hv(e) {
  yp(e, 0);
}
function Sa(e) {
  var t = rs(e);
  if (Th(t)) return e;
}
function Kv(e, t) {
  if (e === 'change') return t;
}
var lp = !1;
if (_n) {
  var Ja;
  if (_n) {
    var eo = 'oninput' in document;
    if (!eo) {
      var yd = document.createElement('div');
      (yd.setAttribute('oninput', 'return;'), (eo = typeof yd.oninput == 'function'));
    }
    Ja = eo;
  } else Ja = !1;
  lp = Ja && (!document.documentMode || 9 < document.documentMode);
}
function vd() {
  pi && (pi.detachEvent('onpropertychange', ap), (Ri = pi = null));
}
function ap(e) {
  if (e.propertyName === 'value' && Sa(Ri)) {
    var t = [];
    (ip(t, Ri, e, qu(e)), Uh(Hv, t));
  }
}
function qv(e, t, n) {
  e === 'focusin'
    ? (vd(), (pi = t), (Ri = n), pi.attachEvent('onpropertychange', ap))
    : e === 'focusout' && vd();
}
function Gv(e) {
  if (e === 'selectionchange' || e === 'keyup' || e === 'keydown') return Sa(Ri);
}
function Yv(e, t) {
  if (e === 'click') return Sa(t);
}
function Xv(e, t) {
  if (e === 'input' || e === 'change') return Sa(t);
}
function Jv(e, t) {
  return (e === t && (e !== 0 || 1 / e === 1 / t)) || (e !== e && t !== t);
}
var Ht = typeof Object.is == 'function' ? Object.is : Jv;
function Ti(e, t) {
  if (Ht(e, t)) return !0;
  if (typeof e != 'object' || e === null || typeof t != 'object' || t === null) return !1;
  var n = Object.keys(e),
    r = Object.keys(t);
  if (n.length !== r.length) return !1;
  for (r = 0; r < n.length; r++) {
    var s = n[r];
    if (!_o.call(t, s) || !Ht(e[s], t[s])) return !1;
  }
  return !0;
}
function gd(e) {
  for (; e && e.firstChild; ) e = e.firstChild;
  return e;
}
function xd(e, t) {
  var n = gd(e);
  e = 0;
  for (var r; n; ) {
    if (n.nodeType === 3) {
      if (((r = e + n.textContent.length), e <= t && r >= t)) return { node: n, offset: t - e };
      e = r;
    }
    e: {
      for (; n; ) {
        if (n.nextSibling) {
          n = n.nextSibling;
          break e;
        }
        n = n.parentNode;
      }
      n = void 0;
    }
    n = gd(n);
  }
}
function op(e, t) {
  return e && t
    ? e === t
      ? !0
      : e && e.nodeType === 3
        ? !1
        : t && t.nodeType === 3
          ? op(e, t.parentNode)
          : 'contains' in e
            ? e.contains(t)
            : e.compareDocumentPosition
              ? !!(e.compareDocumentPosition(t) & 16)
              : !1
    : !1;
}
function up() {
  for (var e = window, t = zl(); t instanceof e.HTMLIFrameElement; ) {
    try {
      var n = typeof t.contentWindow.location.href == 'string';
    } catch {
      n = !1;
    }
    if (n) e = t.contentWindow;
    else break;
    t = zl(e.document);
  }
  return t;
}
function sc(e) {
  var t = e && e.nodeName && e.nodeName.toLowerCase();
  return (
    t &&
    ((t === 'input' &&
      (e.type === 'text' ||
        e.type === 'search' ||
        e.type === 'tel' ||
        e.type === 'url' ||
        e.type === 'password')) ||
      t === 'textarea' ||
      e.contentEditable === 'true')
  );
}
function eg(e) {
  var t = up(),
    n = e.focusedElem,
    r = e.selectionRange;
  if (t !== n && n && n.ownerDocument && op(n.ownerDocument.documentElement, n)) {
    if (r !== null && sc(n)) {
      if (((t = r.start), (e = r.end), e === void 0 && (e = t), 'selectionStart' in n))
        ((n.selectionStart = t), (n.selectionEnd = Math.min(e, n.value.length)));
      else if (
        ((e = ((t = n.ownerDocument || document) && t.defaultView) || window), e.getSelection)
      ) {
        e = e.getSelection();
        var s = n.textContent.length,
          i = Math.min(r.start, s);
        ((r = r.end === void 0 ? i : Math.min(r.end, s)),
          !e.extend && i > r && ((s = r), (r = i), (i = s)),
          (s = xd(n, i)));
        var l = xd(n, r);
        s &&
          l &&
          (e.rangeCount !== 1 ||
            e.anchorNode !== s.node ||
            e.anchorOffset !== s.offset ||
            e.focusNode !== l.node ||
            e.focusOffset !== l.offset) &&
          ((t = t.createRange()),
          t.setStart(s.node, s.offset),
          e.removeAllRanges(),
          i > r
            ? (e.addRange(t), e.extend(l.node, l.offset))
            : (t.setEnd(l.node, l.offset), e.addRange(t)));
      }
    }
    for (t = [], e = n; (e = e.parentNode); )
      e.nodeType === 1 && t.push({ element: e, left: e.scrollLeft, top: e.scrollTop });
    for (typeof n.focus == 'function' && n.focus(), n = 0; n < t.length; n++)
      ((e = t[n]), (e.element.scrollLeft = e.left), (e.element.scrollTop = e.top));
  }
}
var tg = _n && 'documentMode' in document && 11 >= document.documentMode,
  ts = null,
  Uo = null,
  mi = null,
  Vo = !1;
function wd(e, t, n) {
  var r = n.window === n ? n.document : n.nodeType === 9 ? n : n.ownerDocument;
  Vo ||
    ts == null ||
    ts !== zl(r) ||
    ((r = ts),
    'selectionStart' in r && sc(r)
      ? (r = { start: r.selectionStart, end: r.selectionEnd })
      : ((r = ((r.ownerDocument && r.ownerDocument.defaultView) || window).getSelection()),
        (r = {
          anchorNode: r.anchorNode,
          anchorOffset: r.anchorOffset,
          focusNode: r.focusNode,
          focusOffset: r.focusOffset,
        })),
    (mi && Ti(mi, r)) ||
      ((mi = r),
      (r = Zl(Uo, 'onSelect')),
      0 < r.length &&
        ((t = new tc('onSelect', 'select', null, t, n)),
        e.push({ event: t, listeners: r }),
        (t.target = ts))));
}
function ml(e, t) {
  var n = {};
  return (
    (n[e.toLowerCase()] = t.toLowerCase()),
    (n['Webkit' + e] = 'webkit' + t),
    (n['Moz' + e] = 'moz' + t),
    n
  );
}
var ns = {
    animationend: ml('Animation', 'AnimationEnd'),
    animationiteration: ml('Animation', 'AnimationIteration'),
    animationstart: ml('Animation', 'AnimationStart'),
    transitionend: ml('Transition', 'TransitionEnd'),
  },
  to = {},
  cp = {};
_n &&
  ((cp = document.createElement('div').style),
  'AnimationEvent' in window ||
    (delete ns.animationend.animation,
    delete ns.animationiteration.animation,
    delete ns.animationstart.animation),
  'TransitionEvent' in window || delete ns.transitionend.transition);
function Ca(e) {
  if (to[e]) return to[e];
  if (!ns[e]) return e;
  var t = ns[e],
    n;
  for (n in t) if (t.hasOwnProperty(n) && n in cp) return (to[e] = t[n]);
  return e;
}
var dp = Ca('animationend'),
  fp = Ca('animationiteration'),
  hp = Ca('animationstart'),
  pp = Ca('transitionend'),
  mp = new Map(),
  _d =
    'abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel'.split(
      ' ',
    );
function fr(e, t) {
  (mp.set(e, t), Br(t, [e]));
}
for (var no = 0; no < _d.length; no++) {
  var ro = _d[no],
    ng = ro.toLowerCase(),
    rg = ro[0].toUpperCase() + ro.slice(1);
  fr(ng, 'on' + rg);
}
fr(dp, 'onAnimationEnd');
fr(fp, 'onAnimationIteration');
fr(hp, 'onAnimationStart');
fr('dblclick', 'onDoubleClick');
fr('focusin', 'onFocus');
fr('focusout', 'onBlur');
fr(pp, 'onTransitionEnd');
Rs('onMouseEnter', ['mouseout', 'mouseover']);
Rs('onMouseLeave', ['mouseout', 'mouseover']);
Rs('onPointerEnter', ['pointerout', 'pointerover']);
Rs('onPointerLeave', ['pointerout', 'pointerover']);
Br('onChange', 'change click focusin focusout input keydown keyup selectionchange'.split(' '));
Br(
  'onSelect',
  'focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange'.split(' '),
);
Br('onBeforeInput', ['compositionend', 'keypress', 'textInput', 'paste']);
Br('onCompositionEnd', 'compositionend focusout keydown keypress keyup mousedown'.split(' '));
Br('onCompositionStart', 'compositionstart focusout keydown keypress keyup mousedown'.split(' '));
Br('onCompositionUpdate', 'compositionupdate focusout keydown keypress keyup mousedown'.split(' '));
var ai =
    'abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting'.split(
      ' ',
    ),
  sg = new Set('cancel close invalid load scroll toggle'.split(' ').concat(ai));
function kd(e, t, n) {
  var r = e.type || 'unknown-event';
  ((e.currentTarget = n), nv(r, t, void 0, e), (e.currentTarget = null));
}
function yp(e, t) {
  t = (t & 4) !== 0;
  for (var n = 0; n < e.length; n++) {
    var r = e[n],
      s = r.event;
    r = r.listeners;
    e: {
      var i = void 0;
      if (t)
        for (var l = r.length - 1; 0 <= l; l--) {
          var a = r[l],
            o = a.instance,
            u = a.currentTarget;
          if (((a = a.listener), o !== i && s.isPropagationStopped())) break e;
          (kd(s, a, u), (i = o));
        }
      else
        for (l = 0; l < r.length; l++) {
          if (
            ((a = r[l]),
            (o = a.instance),
            (u = a.currentTarget),
            (a = a.listener),
            o !== i && s.isPropagationStopped())
          )
            break e;
          (kd(s, a, u), (i = o));
        }
    }
  }
  if (Vl) throw ((e = Io), (Vl = !1), (Io = null), e);
}
function _e(e, t) {
  var n = t[Zo];
  n === void 0 && (n = t[Zo] = new Set());
  var r = e + '__bubble';
  n.has(r) || (vp(t, e, 2, !1), n.add(r));
}
function so(e, t, n) {
  var r = 0;
  (t && (r |= 4), vp(n, e, r, t));
}
var yl = '_reactListening' + Math.random().toString(36).slice(2);
function Oi(e) {
  if (!e[yl]) {
    ((e[yl] = !0),
      Ch.forEach(function (n) {
        n !== 'selectionchange' && (sg.has(n) || so(n, !1, e), so(n, !0, e));
      }));
    var t = e.nodeType === 9 ? e : e.ownerDocument;
    t === null || t[yl] || ((t[yl] = !0), so('selectionchange', !1, t));
  }
}
function vp(e, t, n, r) {
  switch (ep(t)) {
    case 1:
      var s = gv;
      break;
    case 4:
      s = xv;
      break;
    default:
      s = Ju;
  }
  ((n = s.bind(null, t, n, e)),
    (s = void 0),
    !Fo || (t !== 'touchstart' && t !== 'touchmove' && t !== 'wheel') || (s = !0),
    r
      ? s !== void 0
        ? e.addEventListener(t, n, { capture: !0, passive: s })
        : e.addEventListener(t, n, !0)
      : s !== void 0
        ? e.addEventListener(t, n, { passive: s })
        : e.addEventListener(t, n, !1));
}
function io(e, t, n, r, s) {
  var i = r;
  if (!(t & 1) && !(t & 2) && r !== null)
    e: for (;;) {
      if (r === null) return;
      var l = r.tag;
      if (l === 3 || l === 4) {
        var a = r.stateNode.containerInfo;
        if (a === s || (a.nodeType === 8 && a.parentNode === s)) break;
        if (l === 4)
          for (l = r.return; l !== null; ) {
            var o = l.tag;
            if (
              (o === 3 || o === 4) &&
              ((o = l.stateNode.containerInfo), o === s || (o.nodeType === 8 && o.parentNode === s))
            )
              return;
            l = l.return;
          }
        for (; a !== null; ) {
          if (((l = xr(a)), l === null)) return;
          if (((o = l.tag), o === 5 || o === 6)) {
            r = i = l;
            continue e;
          }
          a = a.parentNode;
        }
      }
      r = r.return;
    }
  Uh(function () {
    var u = i,
      f = qu(n),
      h = [];
    e: {
      var p = mp.get(e);
      if (p !== void 0) {
        var k = tc,
          S = e;
        switch (e) {
          case 'keypress':
            if (Ol(n) === 0) break e;
          case 'keydown':
          case 'keyup':
            k = Lv;
            break;
          case 'focusin':
            ((S = 'focus'), (k = Xa));
            break;
          case 'focusout':
            ((S = 'blur'), (k = Xa));
            break;
          case 'beforeblur':
          case 'afterblur':
            k = Xa;
            break;
          case 'click':
            if (n.button === 2) break e;
          case 'auxclick':
          case 'dblclick':
          case 'mousedown':
          case 'mousemove':
          case 'mouseup':
          case 'mouseout':
          case 'mouseover':
          case 'contextmenu':
            k = cd;
            break;
          case 'drag':
          case 'dragend':
          case 'dragenter':
          case 'dragexit':
          case 'dragleave':
          case 'dragover':
          case 'dragstart':
          case 'drop':
            k = kv;
            break;
          case 'touchcancel':
          case 'touchend':
          case 'touchmove':
          case 'touchstart':
            k = Mv;
            break;
          case dp:
          case fp:
          case hp:
            k = Ev;
            break;
          case pp:
            k = zv;
            break;
          case 'scroll':
            k = wv;
            break;
          case 'wheel':
            k = Vv;
            break;
          case 'copy':
          case 'cut':
          case 'paste':
            k = jv;
            break;
          case 'gotpointercapture':
          case 'lostpointercapture':
          case 'pointercancel':
          case 'pointerdown':
          case 'pointermove':
          case 'pointerout':
          case 'pointerover':
          case 'pointerup':
            k = fd;
        }
        var _ = (t & 4) !== 0,
          N = !_ && e === 'scroll',
          y = _ ? (p !== null ? p + 'Capture' : null) : p;
        _ = [];
        for (var d = u, m; d !== null; ) {
          m = d;
          var x = m.stateNode;
          if (
            (m.tag === 5 &&
              x !== null &&
              ((m = x), y !== null && ((x = Ci(d, y)), x != null && _.push(Pi(d, x, m)))),
            N)
          )
            break;
          d = d.return;
        }
        0 < _.length && ((p = new k(p, S, null, n, f)), h.push({ event: p, listeners: _ }));
      }
    }
    if (!(t & 7)) {
      e: {
        if (
          ((p = e === 'mouseover' || e === 'pointerover'),
          (k = e === 'mouseout' || e === 'pointerout'),
          p && n !== Ao && (S = n.relatedTarget || n.fromElement) && (xr(S) || S[kn]))
        )
          break e;
        if (
          (k || p) &&
          ((p =
            f.window === f ? f : (p = f.ownerDocument) ? p.defaultView || p.parentWindow : window),
          k
            ? ((S = n.relatedTarget || n.toElement),
              (k = u),
              (S = S ? xr(S) : null),
              S !== null && ((N = Qr(S)), S !== N || (S.tag !== 5 && S.tag !== 6)) && (S = null))
            : ((k = null), (S = u)),
          k !== S)
        ) {
          if (
            ((_ = cd),
            (x = 'onMouseLeave'),
            (y = 'onMouseEnter'),
            (d = 'mouse'),
            (e === 'pointerout' || e === 'pointerover') &&
              ((_ = fd), (x = 'onPointerLeave'), (y = 'onPointerEnter'), (d = 'pointer')),
            (N = k == null ? p : rs(k)),
            (m = S == null ? p : rs(S)),
            (p = new _(x, d + 'leave', k, n, f)),
            (p.target = N),
            (p.relatedTarget = m),
            (x = null),
            xr(f) === u &&
              ((_ = new _(y, d + 'enter', S, n, f)),
              (_.target = m),
              (_.relatedTarget = N),
              (x = _)),
            (N = x),
            k && S)
          )
            t: {
              for (_ = k, y = S, d = 0, m = _; m; m = Hr(m)) d++;
              for (m = 0, x = y; x; x = Hr(x)) m++;
              for (; 0 < d - m; ) ((_ = Hr(_)), d--);
              for (; 0 < m - d; ) ((y = Hr(y)), m--);
              for (; d--; ) {
                if (_ === y || (y !== null && _ === y.alternate)) break t;
                ((_ = Hr(_)), (y = Hr(y)));
              }
              _ = null;
            }
          else _ = null;
          (k !== null && Sd(h, p, k, _, !1), S !== null && N !== null && Sd(h, N, S, _, !0));
        }
      }
      e: {
        if (
          ((p = u ? rs(u) : window),
          (k = p.nodeName && p.nodeName.toLowerCase()),
          k === 'select' || (k === 'input' && p.type === 'file'))
        )
          var j = Kv;
        else if (md(p))
          if (lp) j = Xv;
          else {
            j = Gv;
            var O = qv;
          }
        else
          (k = p.nodeName) &&
            k.toLowerCase() === 'input' &&
            (p.type === 'checkbox' || p.type === 'radio') &&
            (j = Yv);
        if (j && (j = j(e, u))) {
          ip(h, j, n, f);
          break e;
        }
        (O && O(e, p, u),
          e === 'focusout' &&
            (O = p._wrapperState) &&
            O.controlled &&
            p.type === 'number' &&
            Ro(p, 'number', p.value));
      }
      switch (((O = u ? rs(u) : window), e)) {
        case 'focusin':
          (md(O) || O.contentEditable === 'true') && ((ts = O), (Uo = u), (mi = null));
          break;
        case 'focusout':
          mi = Uo = ts = null;
          break;
        case 'mousedown':
          Vo = !0;
          break;
        case 'contextmenu':
        case 'mouseup':
        case 'dragend':
          ((Vo = !1), wd(h, n, f));
          break;
        case 'selectionchange':
          if (tg) break;
        case 'keydown':
        case 'keyup':
          wd(h, n, f);
      }
      var A;
      if (rc)
        e: {
          switch (e) {
            case 'compositionstart':
              var L = 'onCompositionStart';
              break e;
            case 'compositionend':
              L = 'onCompositionEnd';
              break e;
            case 'compositionupdate':
              L = 'onCompositionUpdate';
              break e;
          }
          L = void 0;
        }
      else
        es
          ? rp(e, n) && (L = 'onCompositionEnd')
          : e === 'keydown' && n.keyCode === 229 && (L = 'onCompositionStart');
      (L &&
        (np &&
          n.locale !== 'ko' &&
          (es || L !== 'onCompositionStart'
            ? L === 'onCompositionEnd' && es && (A = tp())
            : ((Hn = f), (ec = 'value' in Hn ? Hn.value : Hn.textContent), (es = !0))),
        (O = Zl(u, L)),
        0 < O.length &&
          ((L = new dd(L, e, null, n, f)),
          h.push({ event: L, listeners: O }),
          A ? (L.data = A) : ((A = sp(n)), A !== null && (L.data = A)))),
        (A = Bv ? Qv(e, n) : Wv(e, n)) &&
          ((u = Zl(u, 'onBeforeInput')),
          0 < u.length &&
            ((f = new dd('onBeforeInput', 'beforeinput', null, n, f)),
            h.push({ event: f, listeners: u }),
            (f.data = A))));
    }
    yp(h, t);
  });
}
function Pi(e, t, n) {
  return { instance: e, listener: t, currentTarget: n };
}
function Zl(e, t) {
  for (var n = t + 'Capture', r = []; e !== null; ) {
    var s = e,
      i = s.stateNode;
    (s.tag === 5 &&
      i !== null &&
      ((s = i),
      (i = Ci(e, n)),
      i != null && r.unshift(Pi(e, i, s)),
      (i = Ci(e, t)),
      i != null && r.push(Pi(e, i, s))),
      (e = e.return));
  }
  return r;
}
function Hr(e) {
  if (e === null) return null;
  do e = e.return;
  while (e && e.tag !== 5);
  return e || null;
}
function Sd(e, t, n, r, s) {
  for (var i = t._reactName, l = []; n !== null && n !== r; ) {
    var a = n,
      o = a.alternate,
      u = a.stateNode;
    if (o !== null && o === r) break;
    (a.tag === 5 &&
      u !== null &&
      ((a = u),
      s
        ? ((o = Ci(n, i)), o != null && l.unshift(Pi(n, o, a)))
        : s || ((o = Ci(n, i)), o != null && l.push(Pi(n, o, a)))),
      (n = n.return));
  }
  l.length !== 0 && e.push({ event: t, listeners: l });
}
var ig = /\r\n?/g,
  lg = /\u0000|\uFFFD/g;
function Cd(e) {
  return (typeof e == 'string' ? e : '' + e)
    .replace(
      ig,
      `
`,
    )
    .replace(lg, '');
}
function vl(e, t, n) {
  if (((t = Cd(t)), Cd(e) !== t && n)) throw Error(R(425));
}
function Hl() {}
var $o = null,
  Bo = null;
function Qo(e, t) {
  return (
    e === 'textarea' ||
    e === 'noscript' ||
    typeof t.children == 'string' ||
    typeof t.children == 'number' ||
    (typeof t.dangerouslySetInnerHTML == 'object' &&
      t.dangerouslySetInnerHTML !== null &&
      t.dangerouslySetInnerHTML.__html != null)
  );
}
var Wo = typeof setTimeout == 'function' ? setTimeout : void 0,
  ag = typeof clearTimeout == 'function' ? clearTimeout : void 0,
  Ed = typeof Promise == 'function' ? Promise : void 0,
  og =
    typeof queueMicrotask == 'function'
      ? queueMicrotask
      : typeof Ed < 'u'
        ? function (e) {
            return Ed.resolve(null).then(e).catch(ug);
          }
        : Wo;
function ug(e) {
  setTimeout(function () {
    throw e;
  });
}
function lo(e, t) {
  var n = t,
    r = 0;
  do {
    var s = n.nextSibling;
    if ((e.removeChild(n), s && s.nodeType === 8))
      if (((n = s.data), n === '/$')) {
        if (r === 0) {
          (e.removeChild(s), ji(t));
          return;
        }
        r--;
      } else (n !== '$' && n !== '$?' && n !== '$!') || r++;
    n = s;
  } while (n);
  ji(t);
}
function er(e) {
  for (; e != null; e = e.nextSibling) {
    var t = e.nodeType;
    if (t === 1 || t === 3) break;
    if (t === 8) {
      if (((t = e.data), t === '$' || t === '$!' || t === '$?')) break;
      if (t === '/$') return null;
    }
  }
  return e;
}
function Nd(e) {
  e = e.previousSibling;
  for (var t = 0; e; ) {
    if (e.nodeType === 8) {
      var n = e.data;
      if (n === '$' || n === '$!' || n === '$?') {
        if (t === 0) return e;
        t--;
      } else n === '/$' && t++;
    }
    e = e.previousSibling;
  }
  return null;
}
var Bs = Math.random().toString(36).slice(2),
  nn = '__reactFiber$' + Bs,
  bi = '__reactProps$' + Bs,
  kn = '__reactContainer$' + Bs,
  Zo = '__reactEvents$' + Bs,
  cg = '__reactListeners$' + Bs,
  dg = '__reactHandles$' + Bs;
function xr(e) {
  var t = e[nn];
  if (t) return t;
  for (var n = e.parentNode; n; ) {
    if ((t = n[kn] || n[nn])) {
      if (((n = t.alternate), t.child !== null || (n !== null && n.child !== null)))
        for (e = Nd(e); e !== null; ) {
          if ((n = e[nn])) return n;
          e = Nd(e);
        }
      return t;
    }
    ((e = n), (n = e.parentNode));
  }
  return null;
}
function Xi(e) {
  return (
    (e = e[nn] || e[kn]),
    !e || (e.tag !== 5 && e.tag !== 6 && e.tag !== 13 && e.tag !== 3) ? null : e
  );
}
function rs(e) {
  if (e.tag === 5 || e.tag === 6) return e.stateNode;
  throw Error(R(33));
}
function Ea(e) {
  return e[bi] || null;
}
var Ho = [],
  ss = -1;
function hr(e) {
  return { current: e };
}
function ke(e) {
  0 > ss || ((e.current = Ho[ss]), (Ho[ss] = null), ss--);
}
function we(e, t) {
  (ss++, (Ho[ss] = e.current), (e.current = t));
}
var ur = {},
  et = hr(ur),
  pt = hr(!1),
  Fr = ur;
function Ts(e, t) {
  var n = e.type.contextTypes;
  if (!n) return ur;
  var r = e.stateNode;
  if (r && r.__reactInternalMemoizedUnmaskedChildContext === t)
    return r.__reactInternalMemoizedMaskedChildContext;
  var s = {},
    i;
  for (i in n) s[i] = t[i];
  return (
    r &&
      ((e = e.stateNode),
      (e.__reactInternalMemoizedUnmaskedChildContext = t),
      (e.__reactInternalMemoizedMaskedChildContext = s)),
    s
  );
}
function mt(e) {
  return ((e = e.childContextTypes), e != null);
}
function Kl() {
  (ke(pt), ke(et));
}
function jd(e, t, n) {
  if (et.current !== ur) throw Error(R(168));
  (we(et, t), we(pt, n));
}
function gp(e, t, n) {
  var r = e.stateNode;
  if (((t = t.childContextTypes), typeof r.getChildContext != 'function')) return n;
  r = r.getChildContext();
  for (var s in r) if (!(s in t)) throw Error(R(108, qy(e) || 'Unknown', s));
  return je({}, n, r);
}
function ql(e) {
  return (
    (e = ((e = e.stateNode) && e.__reactInternalMemoizedMergedChildContext) || ur),
    (Fr = et.current),
    we(et, e),
    we(pt, pt.current),
    !0
  );
}
function Rd(e, t, n) {
  var r = e.stateNode;
  if (!r) throw Error(R(169));
  (n
    ? ((e = gp(e, t, Fr)),
      (r.__reactInternalMemoizedMergedChildContext = e),
      ke(pt),
      ke(et),
      we(et, e))
    : ke(pt),
    we(pt, n));
}
var fn = null,
  Na = !1,
  ao = !1;
function xp(e) {
  fn === null ? (fn = [e]) : fn.push(e);
}
function fg(e) {
  ((Na = !0), xp(e));
}
function pr() {
  if (!ao && fn !== null) {
    ao = !0;
    var e = 0,
      t = pe;
    try {
      var n = fn;
      for (pe = 1; e < n.length; e++) {
        var r = n[e];
        do r = r(!0);
        while (r !== null);
      }
      ((fn = null), (Na = !1));
    } catch (s) {
      throw (fn !== null && (fn = fn.slice(e + 1)), Qh(Gu, pr), s);
    } finally {
      ((pe = t), (ao = !1));
    }
  }
  return null;
}
var is = [],
  ls = 0,
  Gl = null,
  Yl = 0,
  Tt = [],
  Ot = 0,
  Ir = null,
  vn = 1,
  gn = '';
function vr(e, t) {
  ((is[ls++] = Yl), (is[ls++] = Gl), (Gl = e), (Yl = t));
}
function wp(e, t, n) {
  ((Tt[Ot++] = vn), (Tt[Ot++] = gn), (Tt[Ot++] = Ir), (Ir = e));
  var r = vn;
  e = gn;
  var s = 32 - Wt(r) - 1;
  ((r &= ~(1 << s)), (n += 1));
  var i = 32 - Wt(t) + s;
  if (30 < i) {
    var l = s - (s % 5);
    ((i = (r & ((1 << l) - 1)).toString(32)),
      (r >>= l),
      (s -= l),
      (vn = (1 << (32 - Wt(t) + s)) | (n << s) | r),
      (gn = i + e));
  } else ((vn = (1 << i) | (n << s) | r), (gn = e));
}
function ic(e) {
  e.return !== null && (vr(e, 1), wp(e, 1, 0));
}
function lc(e) {
  for (; e === Gl; ) ((Gl = is[--ls]), (is[ls] = null), (Yl = is[--ls]), (is[ls] = null));
  for (; e === Ir; )
    ((Ir = Tt[--Ot]),
      (Tt[Ot] = null),
      (gn = Tt[--Ot]),
      (Tt[Ot] = null),
      (vn = Tt[--Ot]),
      (Tt[Ot] = null));
}
var wt = null,
  xt = null,
  Se = !1,
  $t = null;
function _p(e, t) {
  var n = Pt(5, null, null, 0);
  ((n.elementType = 'DELETED'),
    (n.stateNode = t),
    (n.return = e),
    (t = e.deletions),
    t === null ? ((e.deletions = [n]), (e.flags |= 16)) : t.push(n));
}
function Td(e, t) {
  switch (e.tag) {
    case 5:
      var n = e.type;
      return (
        (t = t.nodeType !== 1 || n.toLowerCase() !== t.nodeName.toLowerCase() ? null : t),
        t !== null ? ((e.stateNode = t), (wt = e), (xt = er(t.firstChild)), !0) : !1
      );
    case 6:
      return (
        (t = e.pendingProps === '' || t.nodeType !== 3 ? null : t),
        t !== null ? ((e.stateNode = t), (wt = e), (xt = null), !0) : !1
      );
    case 13:
      return (
        (t = t.nodeType !== 8 ? null : t),
        t !== null
          ? ((n = Ir !== null ? { id: vn, overflow: gn } : null),
            (e.memoizedState = { dehydrated: t, treeContext: n, retryLane: 1073741824 }),
            (n = Pt(18, null, null, 0)),
            (n.stateNode = t),
            (n.return = e),
            (e.child = n),
            (wt = e),
            (xt = null),
            !0)
          : !1
      );
    default:
      return !1;
  }
}
function Ko(e) {
  return (e.mode & 1) !== 0 && (e.flags & 128) === 0;
}
function qo(e) {
  if (Se) {
    var t = xt;
    if (t) {
      var n = t;
      if (!Td(e, t)) {
        if (Ko(e)) throw Error(R(418));
        t = er(n.nextSibling);
        var r = wt;
        t && Td(e, t) ? _p(r, n) : ((e.flags = (e.flags & -4097) | 2), (Se = !1), (wt = e));
      }
    } else {
      if (Ko(e)) throw Error(R(418));
      ((e.flags = (e.flags & -4097) | 2), (Se = !1), (wt = e));
    }
  }
}
function Od(e) {
  for (e = e.return; e !== null && e.tag !== 5 && e.tag !== 3 && e.tag !== 13; ) e = e.return;
  wt = e;
}
function gl(e) {
  if (e !== wt) return !1;
  if (!Se) return (Od(e), (Se = !0), !1);
  var t;
  if (
    ((t = e.tag !== 3) &&
      !(t = e.tag !== 5) &&
      ((t = e.type), (t = t !== 'head' && t !== 'body' && !Qo(e.type, e.memoizedProps))),
    t && (t = xt))
  ) {
    if (Ko(e)) throw (kp(), Error(R(418)));
    for (; t; ) (_p(e, t), (t = er(t.nextSibling)));
  }
  if ((Od(e), e.tag === 13)) {
    if (((e = e.memoizedState), (e = e !== null ? e.dehydrated : null), !e)) throw Error(R(317));
    e: {
      for (e = e.nextSibling, t = 0; e; ) {
        if (e.nodeType === 8) {
          var n = e.data;
          if (n === '/$') {
            if (t === 0) {
              xt = er(e.nextSibling);
              break e;
            }
            t--;
          } else (n !== '$' && n !== '$!' && n !== '$?') || t++;
        }
        e = e.nextSibling;
      }
      xt = null;
    }
  } else xt = wt ? er(e.stateNode.nextSibling) : null;
  return !0;
}
function kp() {
  for (var e = xt; e; ) e = er(e.nextSibling);
}
function Os() {
  ((xt = wt = null), (Se = !1));
}
function ac(e) {
  $t === null ? ($t = [e]) : $t.push(e);
}
var hg = Nn.ReactCurrentBatchConfig;
function Js(e, t, n) {
  if (((e = n.ref), e !== null && typeof e != 'function' && typeof e != 'object')) {
    if (n._owner) {
      if (((n = n._owner), n)) {
        if (n.tag !== 1) throw Error(R(309));
        var r = n.stateNode;
      }
      if (!r) throw Error(R(147, e));
      var s = r,
        i = '' + e;
      return t !== null && t.ref !== null && typeof t.ref == 'function' && t.ref._stringRef === i
        ? t.ref
        : ((t = function (l) {
            var a = s.refs;
            l === null ? delete a[i] : (a[i] = l);
          }),
          (t._stringRef = i),
          t);
    }
    if (typeof e != 'string') throw Error(R(284));
    if (!n._owner) throw Error(R(290, e));
  }
  return e;
}
function xl(e, t) {
  throw (
    (e = Object.prototype.toString.call(t)),
    Error(
      R(31, e === '[object Object]' ? 'object with keys {' + Object.keys(t).join(', ') + '}' : e),
    )
  );
}
function Pd(e) {
  var t = e._init;
  return t(e._payload);
}
function Sp(e) {
  function t(y, d) {
    if (e) {
      var m = y.deletions;
      m === null ? ((y.deletions = [d]), (y.flags |= 16)) : m.push(d);
    }
  }
  function n(y, d) {
    if (!e) return null;
    for (; d !== null; ) (t(y, d), (d = d.sibling));
    return null;
  }
  function r(y, d) {
    for (y = new Map(); d !== null; )
      (d.key !== null ? y.set(d.key, d) : y.set(d.index, d), (d = d.sibling));
    return y;
  }
  function s(y, d) {
    return ((y = sr(y, d)), (y.index = 0), (y.sibling = null), y);
  }
  function i(y, d, m) {
    return (
      (y.index = m),
      e
        ? ((m = y.alternate),
          m !== null ? ((m = m.index), m < d ? ((y.flags |= 2), d) : m) : ((y.flags |= 2), d))
        : ((y.flags |= 1048576), d)
    );
  }
  function l(y) {
    return (e && y.alternate === null && (y.flags |= 2), y);
  }
  function a(y, d, m, x) {
    return d === null || d.tag !== 6
      ? ((d = mo(m, y.mode, x)), (d.return = y), d)
      : ((d = s(d, m)), (d.return = y), d);
  }
  function o(y, d, m, x) {
    var j = m.type;
    return j === Jr
      ? f(y, d, m.props.children, x, m.key)
      : d !== null &&
          (d.elementType === j ||
            (typeof j == 'object' && j !== null && j.$$typeof === bn && Pd(j) === d.type))
        ? ((x = s(d, m.props)), (x.ref = Js(y, d, m)), (x.return = y), x)
        : ((x = Ml(m.type, m.key, m.props, null, y.mode, x)),
          (x.ref = Js(y, d, m)),
          (x.return = y),
          x);
  }
  function u(y, d, m, x) {
    return d === null ||
      d.tag !== 4 ||
      d.stateNode.containerInfo !== m.containerInfo ||
      d.stateNode.implementation !== m.implementation
      ? ((d = yo(m, y.mode, x)), (d.return = y), d)
      : ((d = s(d, m.children || [])), (d.return = y), d);
  }
  function f(y, d, m, x, j) {
    return d === null || d.tag !== 7
      ? ((d = Lr(m, y.mode, x, j)), (d.return = y), d)
      : ((d = s(d, m)), (d.return = y), d);
  }
  function h(y, d, m) {
    if ((typeof d == 'string' && d !== '') || typeof d == 'number')
      return ((d = mo('' + d, y.mode, m)), (d.return = y), d);
    if (typeof d == 'object' && d !== null) {
      switch (d.$$typeof) {
        case ol:
          return (
            (m = Ml(d.type, d.key, d.props, null, y.mode, m)),
            (m.ref = Js(y, null, d)),
            (m.return = y),
            m
          );
        case Xr:
          return ((d = yo(d, y.mode, m)), (d.return = y), d);
        case bn:
          var x = d._init;
          return h(y, x(d._payload), m);
      }
      if (ii(d) || Ks(d)) return ((d = Lr(d, y.mode, m, null)), (d.return = y), d);
      xl(y, d);
    }
    return null;
  }
  function p(y, d, m, x) {
    var j = d !== null ? d.key : null;
    if ((typeof m == 'string' && m !== '') || typeof m == 'number')
      return j !== null ? null : a(y, d, '' + m, x);
    if (typeof m == 'object' && m !== null) {
      switch (m.$$typeof) {
        case ol:
          return m.key === j ? o(y, d, m, x) : null;
        case Xr:
          return m.key === j ? u(y, d, m, x) : null;
        case bn:
          return ((j = m._init), p(y, d, j(m._payload), x));
      }
      if (ii(m) || Ks(m)) return j !== null ? null : f(y, d, m, x, null);
      xl(y, m);
    }
    return null;
  }
  function k(y, d, m, x, j) {
    if ((typeof x == 'string' && x !== '') || typeof x == 'number')
      return ((y = y.get(m) || null), a(d, y, '' + x, j));
    if (typeof x == 'object' && x !== null) {
      switch (x.$$typeof) {
        case ol:
          return ((y = y.get(x.key === null ? m : x.key) || null), o(d, y, x, j));
        case Xr:
          return ((y = y.get(x.key === null ? m : x.key) || null), u(d, y, x, j));
        case bn:
          var O = x._init;
          return k(y, d, m, O(x._payload), j);
      }
      if (ii(x) || Ks(x)) return ((y = y.get(m) || null), f(d, y, x, j, null));
      xl(d, x);
    }
    return null;
  }
  function S(y, d, m, x) {
    for (var j = null, O = null, A = d, L = (d = 0), q = null; A !== null && L < m.length; L++) {
      A.index > L ? ((q = A), (A = null)) : (q = A.sibling);
      var P = p(y, A, m[L], x);
      if (P === null) {
        A === null && (A = q);
        break;
      }
      (e && A && P.alternate === null && t(y, A),
        (d = i(P, d, L)),
        O === null ? (j = P) : (O.sibling = P),
        (O = P),
        (A = q));
    }
    if (L === m.length) return (n(y, A), Se && vr(y, L), j);
    if (A === null) {
      for (; L < m.length; L++)
        ((A = h(y, m[L], x)),
          A !== null && ((d = i(A, d, L)), O === null ? (j = A) : (O.sibling = A), (O = A)));
      return (Se && vr(y, L), j);
    }
    for (A = r(y, A); L < m.length; L++)
      ((q = k(A, y, L, m[L], x)),
        q !== null &&
          (e && q.alternate !== null && A.delete(q.key === null ? L : q.key),
          (d = i(q, d, L)),
          O === null ? (j = q) : (O.sibling = q),
          (O = q)));
    return (
      e &&
        A.forEach(function (H) {
          return t(y, H);
        }),
      Se && vr(y, L),
      j
    );
  }
  function _(y, d, m, x) {
    var j = Ks(m);
    if (typeof j != 'function') throw Error(R(150));
    if (((m = j.call(m)), m == null)) throw Error(R(151));
    for (
      var O = (j = null), A = d, L = (d = 0), q = null, P = m.next();
      A !== null && !P.done;
      L++, P = m.next()
    ) {
      A.index > L ? ((q = A), (A = null)) : (q = A.sibling);
      var H = p(y, A, P.value, x);
      if (H === null) {
        A === null && (A = q);
        break;
      }
      (e && A && H.alternate === null && t(y, A),
        (d = i(H, d, L)),
        O === null ? (j = H) : (O.sibling = H),
        (O = H),
        (A = q));
    }
    if (P.done) return (n(y, A), Se && vr(y, L), j);
    if (A === null) {
      for (; !P.done; L++, P = m.next())
        ((P = h(y, P.value, x)),
          P !== null && ((d = i(P, d, L)), O === null ? (j = P) : (O.sibling = P), (O = P)));
      return (Se && vr(y, L), j);
    }
    for (A = r(y, A); !P.done; L++, P = m.next())
      ((P = k(A, y, L, P.value, x)),
        P !== null &&
          (e && P.alternate !== null && A.delete(P.key === null ? L : P.key),
          (d = i(P, d, L)),
          O === null ? (j = P) : (O.sibling = P),
          (O = P)));
    return (
      e &&
        A.forEach(function (G) {
          return t(y, G);
        }),
      Se && vr(y, L),
      j
    );
  }
  function N(y, d, m, x) {
    if (
      (typeof m == 'object' &&
        m !== null &&
        m.type === Jr &&
        m.key === null &&
        (m = m.props.children),
      typeof m == 'object' && m !== null)
    ) {
      switch (m.$$typeof) {
        case ol:
          e: {
            for (var j = m.key, O = d; O !== null; ) {
              if (O.key === j) {
                if (((j = m.type), j === Jr)) {
                  if (O.tag === 7) {
                    (n(y, O.sibling), (d = s(O, m.props.children)), (d.return = y), (y = d));
                    break e;
                  }
                } else if (
                  O.elementType === j ||
                  (typeof j == 'object' && j !== null && j.$$typeof === bn && Pd(j) === O.type)
                ) {
                  (n(y, O.sibling),
                    (d = s(O, m.props)),
                    (d.ref = Js(y, O, m)),
                    (d.return = y),
                    (y = d));
                  break e;
                }
                n(y, O);
                break;
              } else t(y, O);
              O = O.sibling;
            }
            m.type === Jr
              ? ((d = Lr(m.props.children, y.mode, x, m.key)), (d.return = y), (y = d))
              : ((x = Ml(m.type, m.key, m.props, null, y.mode, x)),
                (x.ref = Js(y, d, m)),
                (x.return = y),
                (y = x));
          }
          return l(y);
        case Xr:
          e: {
            for (O = m.key; d !== null; ) {
              if (d.key === O)
                if (
                  d.tag === 4 &&
                  d.stateNode.containerInfo === m.containerInfo &&
                  d.stateNode.implementation === m.implementation
                ) {
                  (n(y, d.sibling), (d = s(d, m.children || [])), (d.return = y), (y = d));
                  break e;
                } else {
                  n(y, d);
                  break;
                }
              else t(y, d);
              d = d.sibling;
            }
            ((d = yo(m, y.mode, x)), (d.return = y), (y = d));
          }
          return l(y);
        case bn:
          return ((O = m._init), N(y, d, O(m._payload), x));
      }
      if (ii(m)) return S(y, d, m, x);
      if (Ks(m)) return _(y, d, m, x);
      xl(y, m);
    }
    return (typeof m == 'string' && m !== '') || typeof m == 'number'
      ? ((m = '' + m),
        d !== null && d.tag === 6
          ? (n(y, d.sibling), (d = s(d, m)), (d.return = y), (y = d))
          : (n(y, d), (d = mo(m, y.mode, x)), (d.return = y), (y = d)),
        l(y))
      : n(y, d);
  }
  return N;
}
var Ps = Sp(!0),
  Cp = Sp(!1),
  Xl = hr(null),
  Jl = null,
  as = null,
  oc = null;
function uc() {
  oc = as = Jl = null;
}
function cc(e) {
  var t = Xl.current;
  (ke(Xl), (e._currentValue = t));
}
function Go(e, t, n) {
  for (; e !== null; ) {
    var r = e.alternate;
    if (
      ((e.childLanes & t) !== t
        ? ((e.childLanes |= t), r !== null && (r.childLanes |= t))
        : r !== null && (r.childLanes & t) !== t && (r.childLanes |= t),
      e === n)
    )
      break;
    e = e.return;
  }
}
function ps(e, t) {
  ((Jl = e),
    (oc = as = null),
    (e = e.dependencies),
    e !== null && e.firstContext !== null && (e.lanes & t && (ht = !0), (e.firstContext = null)));
}
function At(e) {
  var t = e._currentValue;
  if (oc !== e)
    if (((e = { context: e, memoizedValue: t, next: null }), as === null)) {
      if (Jl === null) throw Error(R(308));
      ((as = e), (Jl.dependencies = { lanes: 0, firstContext: e }));
    } else as = as.next = e;
  return t;
}
var wr = null;
function dc(e) {
  wr === null ? (wr = [e]) : wr.push(e);
}
function Ep(e, t, n, r) {
  var s = t.interleaved;
  return (
    s === null ? ((n.next = n), dc(t)) : ((n.next = s.next), (s.next = n)),
    (t.interleaved = n),
    Sn(e, r)
  );
}
function Sn(e, t) {
  e.lanes |= t;
  var n = e.alternate;
  for (n !== null && (n.lanes |= t), n = e, e = e.return; e !== null; )
    ((e.childLanes |= t),
      (n = e.alternate),
      n !== null && (n.childLanes |= t),
      (n = e),
      (e = e.return));
  return n.tag === 3 ? n.stateNode : null;
}
var An = !1;
function fc(e) {
  e.updateQueue = {
    baseState: e.memoizedState,
    firstBaseUpdate: null,
    lastBaseUpdate: null,
    shared: { pending: null, interleaved: null, lanes: 0 },
    effects: null,
  };
}
function Np(e, t) {
  ((e = e.updateQueue),
    t.updateQueue === e &&
      (t.updateQueue = {
        baseState: e.baseState,
        firstBaseUpdate: e.firstBaseUpdate,
        lastBaseUpdate: e.lastBaseUpdate,
        shared: e.shared,
        effects: e.effects,
      }));
}
function xn(e, t) {
  return { eventTime: e, lane: t, tag: 0, payload: null, callback: null, next: null };
}
function tr(e, t, n) {
  var r = e.updateQueue;
  if (r === null) return null;
  if (((r = r.shared), oe & 2)) {
    var s = r.pending;
    return (
      s === null ? (t.next = t) : ((t.next = s.next), (s.next = t)),
      (r.pending = t),
      Sn(e, n)
    );
  }
  return (
    (s = r.interleaved),
    s === null ? ((t.next = t), dc(r)) : ((t.next = s.next), (s.next = t)),
    (r.interleaved = t),
    Sn(e, n)
  );
}
function Pl(e, t, n) {
  if (((t = t.updateQueue), t !== null && ((t = t.shared), (n & 4194240) !== 0))) {
    var r = t.lanes;
    ((r &= e.pendingLanes), (n |= r), (t.lanes = n), Yu(e, n));
  }
}
function bd(e, t) {
  var n = e.updateQueue,
    r = e.alternate;
  if (r !== null && ((r = r.updateQueue), n === r)) {
    var s = null,
      i = null;
    if (((n = n.firstBaseUpdate), n !== null)) {
      do {
        var l = {
          eventTime: n.eventTime,
          lane: n.lane,
          tag: n.tag,
          payload: n.payload,
          callback: n.callback,
          next: null,
        };
        (i === null ? (s = i = l) : (i = i.next = l), (n = n.next));
      } while (n !== null);
      i === null ? (s = i = t) : (i = i.next = t);
    } else s = i = t;
    ((n = {
      baseState: r.baseState,
      firstBaseUpdate: s,
      lastBaseUpdate: i,
      shared: r.shared,
      effects: r.effects,
    }),
      (e.updateQueue = n));
    return;
  }
  ((e = n.lastBaseUpdate),
    e === null ? (n.firstBaseUpdate = t) : (e.next = t),
    (n.lastBaseUpdate = t));
}
function ea(e, t, n, r) {
  var s = e.updateQueue;
  An = !1;
  var i = s.firstBaseUpdate,
    l = s.lastBaseUpdate,
    a = s.shared.pending;
  if (a !== null) {
    s.shared.pending = null;
    var o = a,
      u = o.next;
    ((o.next = null), l === null ? (i = u) : (l.next = u), (l = o));
    var f = e.alternate;
    f !== null &&
      ((f = f.updateQueue),
      (a = f.lastBaseUpdate),
      a !== l && (a === null ? (f.firstBaseUpdate = u) : (a.next = u), (f.lastBaseUpdate = o)));
  }
  if (i !== null) {
    var h = s.baseState;
    ((l = 0), (f = u = o = null), (a = i));
    do {
      var p = a.lane,
        k = a.eventTime;
      if ((r & p) === p) {
        f !== null &&
          (f = f.next =
            {
              eventTime: k,
              lane: 0,
              tag: a.tag,
              payload: a.payload,
              callback: a.callback,
              next: null,
            });
        e: {
          var S = e,
            _ = a;
          switch (((p = t), (k = n), _.tag)) {
            case 1:
              if (((S = _.payload), typeof S == 'function')) {
                h = S.call(k, h, p);
                break e;
              }
              h = S;
              break e;
            case 3:
              S.flags = (S.flags & -65537) | 128;
            case 0:
              if (((S = _.payload), (p = typeof S == 'function' ? S.call(k, h, p) : S), p == null))
                break e;
              h = je({}, h, p);
              break e;
            case 2:
              An = !0;
          }
        }
        a.callback !== null &&
          a.lane !== 0 &&
          ((e.flags |= 64), (p = s.effects), p === null ? (s.effects = [a]) : p.push(a));
      } else
        ((k = {
          eventTime: k,
          lane: p,
          tag: a.tag,
          payload: a.payload,
          callback: a.callback,
          next: null,
        }),
          f === null ? ((u = f = k), (o = h)) : (f = f.next = k),
          (l |= p));
      if (((a = a.next), a === null)) {
        if (((a = s.shared.pending), a === null)) break;
        ((p = a), (a = p.next), (p.next = null), (s.lastBaseUpdate = p), (s.shared.pending = null));
      }
    } while (!0);
    if (
      (f === null && (o = h),
      (s.baseState = o),
      (s.firstBaseUpdate = u),
      (s.lastBaseUpdate = f),
      (t = s.shared.interleaved),
      t !== null)
    ) {
      s = t;
      do ((l |= s.lane), (s = s.next));
      while (s !== t);
    } else i === null && (s.shared.lanes = 0);
    ((Dr |= l), (e.lanes = l), (e.memoizedState = h));
  }
}
function Ad(e, t, n) {
  if (((e = t.effects), (t.effects = null), e !== null))
    for (t = 0; t < e.length; t++) {
      var r = e[t],
        s = r.callback;
      if (s !== null) {
        if (((r.callback = null), (r = n), typeof s != 'function')) throw Error(R(191, s));
        s.call(r);
      }
    }
}
var Ji = {},
  sn = hr(Ji),
  Ai = hr(Ji),
  Li = hr(Ji);
function _r(e) {
  if (e === Ji) throw Error(R(174));
  return e;
}
function hc(e, t) {
  switch ((we(Li, t), we(Ai, e), we(sn, Ji), (e = t.nodeType), e)) {
    case 9:
    case 11:
      t = (t = t.documentElement) ? t.namespaceURI : Oo(null, '');
      break;
    default:
      ((e = e === 8 ? t.parentNode : t),
        (t = e.namespaceURI || null),
        (e = e.tagName),
        (t = Oo(t, e)));
  }
  (ke(sn), we(sn, t));
}
function bs() {
  (ke(sn), ke(Ai), ke(Li));
}
function jp(e) {
  _r(Li.current);
  var t = _r(sn.current),
    n = Oo(t, e.type);
  t !== n && (we(Ai, e), we(sn, n));
}
function pc(e) {
  Ai.current === e && (ke(sn), ke(Ai));
}
var Ee = hr(0);
function ta(e) {
  for (var t = e; t !== null; ) {
    if (t.tag === 13) {
      var n = t.memoizedState;
      if (n !== null && ((n = n.dehydrated), n === null || n.data === '$?' || n.data === '$!'))
        return t;
    } else if (t.tag === 19 && t.memoizedProps.revealOrder !== void 0) {
      if (t.flags & 128) return t;
    } else if (t.child !== null) {
      ((t.child.return = t), (t = t.child));
      continue;
    }
    if (t === e) break;
    for (; t.sibling === null; ) {
      if (t.return === null || t.return === e) return null;
      t = t.return;
    }
    ((t.sibling.return = t.return), (t = t.sibling));
  }
  return null;
}
var oo = [];
function mc() {
  for (var e = 0; e < oo.length; e++) oo[e]._workInProgressVersionPrimary = null;
  oo.length = 0;
}
var bl = Nn.ReactCurrentDispatcher,
  uo = Nn.ReactCurrentBatchConfig,
  Mr = 0,
  Ne = null,
  De = null,
  Qe = null,
  na = !1,
  yi = !1,
  Fi = 0,
  pg = 0;
function Ge() {
  throw Error(R(321));
}
function yc(e, t) {
  if (t === null) return !1;
  for (var n = 0; n < t.length && n < e.length; n++) if (!Ht(e[n], t[n])) return !1;
  return !0;
}
function vc(e, t, n, r, s, i) {
  if (
    ((Mr = i),
    (Ne = t),
    (t.memoizedState = null),
    (t.updateQueue = null),
    (t.lanes = 0),
    (bl.current = e === null || e.memoizedState === null ? gg : xg),
    (e = n(r, s)),
    yi)
  ) {
    i = 0;
    do {
      if (((yi = !1), (Fi = 0), 25 <= i)) throw Error(R(301));
      ((i += 1), (Qe = De = null), (t.updateQueue = null), (bl.current = wg), (e = n(r, s)));
    } while (yi);
  }
  if (
    ((bl.current = ra),
    (t = De !== null && De.next !== null),
    (Mr = 0),
    (Qe = De = Ne = null),
    (na = !1),
    t)
  )
    throw Error(R(300));
  return e;
}
function gc() {
  var e = Fi !== 0;
  return ((Fi = 0), e);
}
function Yt() {
  var e = { memoizedState: null, baseState: null, baseQueue: null, queue: null, next: null };
  return (Qe === null ? (Ne.memoizedState = Qe = e) : (Qe = Qe.next = e), Qe);
}
function Lt() {
  if (De === null) {
    var e = Ne.alternate;
    e = e !== null ? e.memoizedState : null;
  } else e = De.next;
  var t = Qe === null ? Ne.memoizedState : Qe.next;
  if (t !== null) ((Qe = t), (De = e));
  else {
    if (e === null) throw Error(R(310));
    ((De = e),
      (e = {
        memoizedState: De.memoizedState,
        baseState: De.baseState,
        baseQueue: De.baseQueue,
        queue: De.queue,
        next: null,
      }),
      Qe === null ? (Ne.memoizedState = Qe = e) : (Qe = Qe.next = e));
  }
  return Qe;
}
function Ii(e, t) {
  return typeof t == 'function' ? t(e) : t;
}
function co(e) {
  var t = Lt(),
    n = t.queue;
  if (n === null) throw Error(R(311));
  n.lastRenderedReducer = e;
  var r = De,
    s = r.baseQueue,
    i = n.pending;
  if (i !== null) {
    if (s !== null) {
      var l = s.next;
      ((s.next = i.next), (i.next = l));
    }
    ((r.baseQueue = s = i), (n.pending = null));
  }
  if (s !== null) {
    ((i = s.next), (r = r.baseState));
    var a = (l = null),
      o = null,
      u = i;
    do {
      var f = u.lane;
      if ((Mr & f) === f)
        (o !== null &&
          (o = o.next =
            {
              lane: 0,
              action: u.action,
              hasEagerState: u.hasEagerState,
              eagerState: u.eagerState,
              next: null,
            }),
          (r = u.hasEagerState ? u.eagerState : e(r, u.action)));
      else {
        var h = {
          lane: f,
          action: u.action,
          hasEagerState: u.hasEagerState,
          eagerState: u.eagerState,
          next: null,
        };
        (o === null ? ((a = o = h), (l = r)) : (o = o.next = h), (Ne.lanes |= f), (Dr |= f));
      }
      u = u.next;
    } while (u !== null && u !== i);
    (o === null ? (l = r) : (o.next = a),
      Ht(r, t.memoizedState) || (ht = !0),
      (t.memoizedState = r),
      (t.baseState = l),
      (t.baseQueue = o),
      (n.lastRenderedState = r));
  }
  if (((e = n.interleaved), e !== null)) {
    s = e;
    do ((i = s.lane), (Ne.lanes |= i), (Dr |= i), (s = s.next));
    while (s !== e);
  } else s === null && (n.lanes = 0);
  return [t.memoizedState, n.dispatch];
}
function fo(e) {
  var t = Lt(),
    n = t.queue;
  if (n === null) throw Error(R(311));
  n.lastRenderedReducer = e;
  var r = n.dispatch,
    s = n.pending,
    i = t.memoizedState;
  if (s !== null) {
    n.pending = null;
    var l = (s = s.next);
    do ((i = e(i, l.action)), (l = l.next));
    while (l !== s);
    (Ht(i, t.memoizedState) || (ht = !0),
      (t.memoizedState = i),
      t.baseQueue === null && (t.baseState = i),
      (n.lastRenderedState = i));
  }
  return [i, r];
}
function Rp() {}
function Tp(e, t) {
  var n = Ne,
    r = Lt(),
    s = t(),
    i = !Ht(r.memoizedState, s);
  if (
    (i && ((r.memoizedState = s), (ht = !0)),
    (r = r.queue),
    xc(bp.bind(null, n, r, e), [e]),
    r.getSnapshot !== t || i || (Qe !== null && Qe.memoizedState.tag & 1))
  ) {
    if (((n.flags |= 2048), Mi(9, Pp.bind(null, n, r, s, t), void 0, null), We === null))
      throw Error(R(349));
    Mr & 30 || Op(n, t, s);
  }
  return s;
}
function Op(e, t, n) {
  ((e.flags |= 16384),
    (e = { getSnapshot: t, value: n }),
    (t = Ne.updateQueue),
    t === null
      ? ((t = { lastEffect: null, stores: null }), (Ne.updateQueue = t), (t.stores = [e]))
      : ((n = t.stores), n === null ? (t.stores = [e]) : n.push(e)));
}
function Pp(e, t, n, r) {
  ((t.value = n), (t.getSnapshot = r), Ap(t) && Lp(e));
}
function bp(e, t, n) {
  return n(function () {
    Ap(t) && Lp(e);
  });
}
function Ap(e) {
  var t = e.getSnapshot;
  e = e.value;
  try {
    var n = t();
    return !Ht(e, n);
  } catch {
    return !0;
  }
}
function Lp(e) {
  var t = Sn(e, 1);
  t !== null && Zt(t, e, 1, -1);
}
function Ld(e) {
  var t = Yt();
  return (
    typeof e == 'function' && (e = e()),
    (t.memoizedState = t.baseState = e),
    (e = {
      pending: null,
      interleaved: null,
      lanes: 0,
      dispatch: null,
      lastRenderedReducer: Ii,
      lastRenderedState: e,
    }),
    (t.queue = e),
    (e = e.dispatch = vg.bind(null, Ne, e)),
    [t.memoizedState, e]
  );
}
function Mi(e, t, n, r) {
  return (
    (e = { tag: e, create: t, destroy: n, deps: r, next: null }),
    (t = Ne.updateQueue),
    t === null
      ? ((t = { lastEffect: null, stores: null }),
        (Ne.updateQueue = t),
        (t.lastEffect = e.next = e))
      : ((n = t.lastEffect),
        n === null
          ? (t.lastEffect = e.next = e)
          : ((r = n.next), (n.next = e), (e.next = r), (t.lastEffect = e))),
    e
  );
}
function Fp() {
  return Lt().memoizedState;
}
function Al(e, t, n, r) {
  var s = Yt();
  ((Ne.flags |= e), (s.memoizedState = Mi(1 | t, n, void 0, r === void 0 ? null : r)));
}
function ja(e, t, n, r) {
  var s = Lt();
  r = r === void 0 ? null : r;
  var i = void 0;
  if (De !== null) {
    var l = De.memoizedState;
    if (((i = l.destroy), r !== null && yc(r, l.deps))) {
      s.memoizedState = Mi(t, n, i, r);
      return;
    }
  }
  ((Ne.flags |= e), (s.memoizedState = Mi(1 | t, n, i, r)));
}
function Fd(e, t) {
  return Al(8390656, 8, e, t);
}
function xc(e, t) {
  return ja(2048, 8, e, t);
}
function Ip(e, t) {
  return ja(4, 2, e, t);
}
function Mp(e, t) {
  return ja(4, 4, e, t);
}
function Dp(e, t) {
  if (typeof t == 'function')
    return (
      (e = e()),
      t(e),
      function () {
        t(null);
      }
    );
  if (t != null)
    return (
      (e = e()),
      (t.current = e),
      function () {
        t.current = null;
      }
    );
}
function zp(e, t, n) {
  return ((n = n != null ? n.concat([e]) : null), ja(4, 4, Dp.bind(null, t, e), n));
}
function wc() {}
function Up(e, t) {
  var n = Lt();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null && t !== null && yc(t, r[1]) ? r[0] : ((n.memoizedState = [e, t]), e);
}
function Vp(e, t) {
  var n = Lt();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null && t !== null && yc(t, r[1])
    ? r[0]
    : ((e = e()), (n.memoizedState = [e, t]), e);
}
function $p(e, t, n) {
  return Mr & 21
    ? (Ht(n, t) || ((n = Hh()), (Ne.lanes |= n), (Dr |= n), (e.baseState = !0)), t)
    : (e.baseState && ((e.baseState = !1), (ht = !0)), (e.memoizedState = n));
}
function mg(e, t) {
  var n = pe;
  ((pe = n !== 0 && 4 > n ? n : 4), e(!0));
  var r = uo.transition;
  uo.transition = {};
  try {
    (e(!1), t());
  } finally {
    ((pe = n), (uo.transition = r));
  }
}
function Bp() {
  return Lt().memoizedState;
}
function yg(e, t, n) {
  var r = rr(e);
  if (((n = { lane: r, action: n, hasEagerState: !1, eagerState: null, next: null }), Qp(e)))
    Wp(t, n);
  else if (((n = Ep(e, t, n, r)), n !== null)) {
    var s = lt();
    (Zt(n, e, r, s), Zp(n, t, r));
  }
}
function vg(e, t, n) {
  var r = rr(e),
    s = { lane: r, action: n, hasEagerState: !1, eagerState: null, next: null };
  if (Qp(e)) Wp(t, s);
  else {
    var i = e.alternate;
    if (e.lanes === 0 && (i === null || i.lanes === 0) && ((i = t.lastRenderedReducer), i !== null))
      try {
        var l = t.lastRenderedState,
          a = i(l, n);
        if (((s.hasEagerState = !0), (s.eagerState = a), Ht(a, l))) {
          var o = t.interleaved;
          (o === null ? ((s.next = s), dc(t)) : ((s.next = o.next), (o.next = s)),
            (t.interleaved = s));
          return;
        }
      } catch {
      } finally {
      }
    ((n = Ep(e, t, s, r)), n !== null && ((s = lt()), Zt(n, e, r, s), Zp(n, t, r)));
  }
}
function Qp(e) {
  var t = e.alternate;
  return e === Ne || (t !== null && t === Ne);
}
function Wp(e, t) {
  yi = na = !0;
  var n = e.pending;
  (n === null ? (t.next = t) : ((t.next = n.next), (n.next = t)), (e.pending = t));
}
function Zp(e, t, n) {
  if (n & 4194240) {
    var r = t.lanes;
    ((r &= e.pendingLanes), (n |= r), (t.lanes = n), Yu(e, n));
  }
}
var ra = {
    readContext: At,
    useCallback: Ge,
    useContext: Ge,
    useEffect: Ge,
    useImperativeHandle: Ge,
    useInsertionEffect: Ge,
    useLayoutEffect: Ge,
    useMemo: Ge,
    useReducer: Ge,
    useRef: Ge,
    useState: Ge,
    useDebugValue: Ge,
    useDeferredValue: Ge,
    useTransition: Ge,
    useMutableSource: Ge,
    useSyncExternalStore: Ge,
    useId: Ge,
    unstable_isNewReconciler: !1,
  },
  gg = {
    readContext: At,
    useCallback: function (e, t) {
      return ((Yt().memoizedState = [e, t === void 0 ? null : t]), e);
    },
    useContext: At,
    useEffect: Fd,
    useImperativeHandle: function (e, t, n) {
      return ((n = n != null ? n.concat([e]) : null), Al(4194308, 4, Dp.bind(null, t, e), n));
    },
    useLayoutEffect: function (e, t) {
      return Al(4194308, 4, e, t);
    },
    useInsertionEffect: function (e, t) {
      return Al(4, 2, e, t);
    },
    useMemo: function (e, t) {
      var n = Yt();
      return ((t = t === void 0 ? null : t), (e = e()), (n.memoizedState = [e, t]), e);
    },
    useReducer: function (e, t, n) {
      var r = Yt();
      return (
        (t = n !== void 0 ? n(t) : t),
        (r.memoizedState = r.baseState = t),
        (e = {
          pending: null,
          interleaved: null,
          lanes: 0,
          dispatch: null,
          lastRenderedReducer: e,
          lastRenderedState: t,
        }),
        (r.queue = e),
        (e = e.dispatch = yg.bind(null, Ne, e)),
        [r.memoizedState, e]
      );
    },
    useRef: function (e) {
      var t = Yt();
      return ((e = { current: e }), (t.memoizedState = e));
    },
    useState: Ld,
    useDebugValue: wc,
    useDeferredValue: function (e) {
      return (Yt().memoizedState = e);
    },
    useTransition: function () {
      var e = Ld(!1),
        t = e[0];
      return ((e = mg.bind(null, e[1])), (Yt().memoizedState = e), [t, e]);
    },
    useMutableSource: function () {},
    useSyncExternalStore: function (e, t, n) {
      var r = Ne,
        s = Yt();
      if (Se) {
        if (n === void 0) throw Error(R(407));
        n = n();
      } else {
        if (((n = t()), We === null)) throw Error(R(349));
        Mr & 30 || Op(r, t, n);
      }
      s.memoizedState = n;
      var i = { value: n, getSnapshot: t };
      return (
        (s.queue = i),
        Fd(bp.bind(null, r, i, e), [e]),
        (r.flags |= 2048),
        Mi(9, Pp.bind(null, r, i, n, t), void 0, null),
        n
      );
    },
    useId: function () {
      var e = Yt(),
        t = We.identifierPrefix;
      if (Se) {
        var n = gn,
          r = vn;
        ((n = (r & ~(1 << (32 - Wt(r) - 1))).toString(32) + n),
          (t = ':' + t + 'R' + n),
          (n = Fi++),
          0 < n && (t += 'H' + n.toString(32)),
          (t += ':'));
      } else ((n = pg++), (t = ':' + t + 'r' + n.toString(32) + ':'));
      return (e.memoizedState = t);
    },
    unstable_isNewReconciler: !1,
  },
  xg = {
    readContext: At,
    useCallback: Up,
    useContext: At,
    useEffect: xc,
    useImperativeHandle: zp,
    useInsertionEffect: Ip,
    useLayoutEffect: Mp,
    useMemo: Vp,
    useReducer: co,
    useRef: Fp,
    useState: function () {
      return co(Ii);
    },
    useDebugValue: wc,
    useDeferredValue: function (e) {
      var t = Lt();
      return $p(t, De.memoizedState, e);
    },
    useTransition: function () {
      var e = co(Ii)[0],
        t = Lt().memoizedState;
      return [e, t];
    },
    useMutableSource: Rp,
    useSyncExternalStore: Tp,
    useId: Bp,
    unstable_isNewReconciler: !1,
  },
  wg = {
    readContext: At,
    useCallback: Up,
    useContext: At,
    useEffect: xc,
    useImperativeHandle: zp,
    useInsertionEffect: Ip,
    useLayoutEffect: Mp,
    useMemo: Vp,
    useReducer: fo,
    useRef: Fp,
    useState: function () {
      return fo(Ii);
    },
    useDebugValue: wc,
    useDeferredValue: function (e) {
      var t = Lt();
      return De === null ? (t.memoizedState = e) : $p(t, De.memoizedState, e);
    },
    useTransition: function () {
      var e = fo(Ii)[0],
        t = Lt().memoizedState;
      return [e, t];
    },
    useMutableSource: Rp,
    useSyncExternalStore: Tp,
    useId: Bp,
    unstable_isNewReconciler: !1,
  };
function Dt(e, t) {
  if (e && e.defaultProps) {
    ((t = je({}, t)), (e = e.defaultProps));
    for (var n in e) t[n] === void 0 && (t[n] = e[n]);
    return t;
  }
  return t;
}
function Yo(e, t, n, r) {
  ((t = e.memoizedState),
    (n = n(r, t)),
    (n = n == null ? t : je({}, t, n)),
    (e.memoizedState = n),
    e.lanes === 0 && (e.updateQueue.baseState = n));
}
var Ra = {
  isMounted: function (e) {
    return (e = e._reactInternals) ? Qr(e) === e : !1;
  },
  enqueueSetState: function (e, t, n) {
    e = e._reactInternals;
    var r = lt(),
      s = rr(e),
      i = xn(r, s);
    ((i.payload = t),
      n != null && (i.callback = n),
      (t = tr(e, i, s)),
      t !== null && (Zt(t, e, s, r), Pl(t, e, s)));
  },
  enqueueReplaceState: function (e, t, n) {
    e = e._reactInternals;
    var r = lt(),
      s = rr(e),
      i = xn(r, s);
    ((i.tag = 1),
      (i.payload = t),
      n != null && (i.callback = n),
      (t = tr(e, i, s)),
      t !== null && (Zt(t, e, s, r), Pl(t, e, s)));
  },
  enqueueForceUpdate: function (e, t) {
    e = e._reactInternals;
    var n = lt(),
      r = rr(e),
      s = xn(n, r);
    ((s.tag = 2),
      t != null && (s.callback = t),
      (t = tr(e, s, r)),
      t !== null && (Zt(t, e, r, n), Pl(t, e, r)));
  },
};
function Id(e, t, n, r, s, i, l) {
  return (
    (e = e.stateNode),
    typeof e.shouldComponentUpdate == 'function'
      ? e.shouldComponentUpdate(r, i, l)
      : t.prototype && t.prototype.isPureReactComponent
        ? !Ti(n, r) || !Ti(s, i)
        : !0
  );
}
function Hp(e, t, n) {
  var r = !1,
    s = ur,
    i = t.contextType;
  return (
    typeof i == 'object' && i !== null
      ? (i = At(i))
      : ((s = mt(t) ? Fr : et.current),
        (r = t.contextTypes),
        (i = (r = r != null) ? Ts(e, s) : ur)),
    (t = new t(n, i)),
    (e.memoizedState = t.state !== null && t.state !== void 0 ? t.state : null),
    (t.updater = Ra),
    (e.stateNode = t),
    (t._reactInternals = e),
    r &&
      ((e = e.stateNode),
      (e.__reactInternalMemoizedUnmaskedChildContext = s),
      (e.__reactInternalMemoizedMaskedChildContext = i)),
    t
  );
}
function Md(e, t, n, r) {
  ((e = t.state),
    typeof t.componentWillReceiveProps == 'function' && t.componentWillReceiveProps(n, r),
    typeof t.UNSAFE_componentWillReceiveProps == 'function' &&
      t.UNSAFE_componentWillReceiveProps(n, r),
    t.state !== e && Ra.enqueueReplaceState(t, t.state, null));
}
function Xo(e, t, n, r) {
  var s = e.stateNode;
  ((s.props = n), (s.state = e.memoizedState), (s.refs = {}), fc(e));
  var i = t.contextType;
  (typeof i == 'object' && i !== null
    ? (s.context = At(i))
    : ((i = mt(t) ? Fr : et.current), (s.context = Ts(e, i))),
    (s.state = e.memoizedState),
    (i = t.getDerivedStateFromProps),
    typeof i == 'function' && (Yo(e, t, i, n), (s.state = e.memoizedState)),
    typeof t.getDerivedStateFromProps == 'function' ||
      typeof s.getSnapshotBeforeUpdate == 'function' ||
      (typeof s.UNSAFE_componentWillMount != 'function' &&
        typeof s.componentWillMount != 'function') ||
      ((t = s.state),
      typeof s.componentWillMount == 'function' && s.componentWillMount(),
      typeof s.UNSAFE_componentWillMount == 'function' && s.UNSAFE_componentWillMount(),
      t !== s.state && Ra.enqueueReplaceState(s, s.state, null),
      ea(e, n, s, r),
      (s.state = e.memoizedState)),
    typeof s.componentDidMount == 'function' && (e.flags |= 4194308));
}
function As(e, t) {
  try {
    var n = '',
      r = t;
    do ((n += Ky(r)), (r = r.return));
    while (r);
    var s = n;
  } catch (i) {
    s =
      `
Error generating stack: ` +
      i.message +
      `
` +
      i.stack;
  }
  return { value: e, source: t, stack: s, digest: null };
}
function ho(e, t, n) {
  return { value: e, source: null, stack: n ?? null, digest: t ?? null };
}
function Jo(e, t) {
  try {
    console.error(t.value);
  } catch (n) {
    setTimeout(function () {
      throw n;
    });
  }
}
var _g = typeof WeakMap == 'function' ? WeakMap : Map;
function Kp(e, t, n) {
  ((n = xn(-1, n)), (n.tag = 3), (n.payload = { element: null }));
  var r = t.value;
  return (
    (n.callback = function () {
      (ia || ((ia = !0), (uu = r)), Jo(e, t));
    }),
    n
  );
}
function qp(e, t, n) {
  ((n = xn(-1, n)), (n.tag = 3));
  var r = e.type.getDerivedStateFromError;
  if (typeof r == 'function') {
    var s = t.value;
    ((n.payload = function () {
      return r(s);
    }),
      (n.callback = function () {
        Jo(e, t);
      }));
  }
  var i = e.stateNode;
  return (
    i !== null &&
      typeof i.componentDidCatch == 'function' &&
      (n.callback = function () {
        (Jo(e, t), typeof r != 'function' && (nr === null ? (nr = new Set([this])) : nr.add(this)));
        var l = t.stack;
        this.componentDidCatch(t.value, { componentStack: l !== null ? l : '' });
      }),
    n
  );
}
function Dd(e, t, n) {
  var r = e.pingCache;
  if (r === null) {
    r = e.pingCache = new _g();
    var s = new Set();
    r.set(t, s);
  } else ((s = r.get(t)), s === void 0 && ((s = new Set()), r.set(t, s)));
  s.has(n) || (s.add(n), (e = Fg.bind(null, e, t, n)), t.then(e, e));
}
function zd(e) {
  do {
    var t;
    if (
      ((t = e.tag === 13) && ((t = e.memoizedState), (t = t !== null ? t.dehydrated !== null : !0)),
      t)
    )
      return e;
    e = e.return;
  } while (e !== null);
  return null;
}
function Ud(e, t, n, r, s) {
  return e.mode & 1
    ? ((e.flags |= 65536), (e.lanes = s), e)
    : (e === t
        ? (e.flags |= 65536)
        : ((e.flags |= 128),
          (n.flags |= 131072),
          (n.flags &= -52805),
          n.tag === 1 &&
            (n.alternate === null ? (n.tag = 17) : ((t = xn(-1, 1)), (t.tag = 2), tr(n, t, 1))),
          (n.lanes |= 1)),
      e);
}
var kg = Nn.ReactCurrentOwner,
  ht = !1;
function rt(e, t, n, r) {
  t.child = e === null ? Cp(t, null, n, r) : Ps(t, e.child, n, r);
}
function Vd(e, t, n, r, s) {
  n = n.render;
  var i = t.ref;
  return (
    ps(t, s),
    (r = vc(e, t, n, r, i, s)),
    (n = gc()),
    e !== null && !ht
      ? ((t.updateQueue = e.updateQueue), (t.flags &= -2053), (e.lanes &= ~s), Cn(e, t, s))
      : (Se && n && ic(t), (t.flags |= 1), rt(e, t, r, s), t.child)
  );
}
function $d(e, t, n, r, s) {
  if (e === null) {
    var i = n.type;
    return typeof i == 'function' &&
      !Rc(i) &&
      i.defaultProps === void 0 &&
      n.compare === null &&
      n.defaultProps === void 0
      ? ((t.tag = 15), (t.type = i), Gp(e, t, i, r, s))
      : ((e = Ml(n.type, null, r, t, t.mode, s)), (e.ref = t.ref), (e.return = t), (t.child = e));
  }
  if (((i = e.child), !(e.lanes & s))) {
    var l = i.memoizedProps;
    if (((n = n.compare), (n = n !== null ? n : Ti), n(l, r) && e.ref === t.ref))
      return Cn(e, t, s);
  }
  return ((t.flags |= 1), (e = sr(i, r)), (e.ref = t.ref), (e.return = t), (t.child = e));
}
function Gp(e, t, n, r, s) {
  if (e !== null) {
    var i = e.memoizedProps;
    if (Ti(i, r) && e.ref === t.ref)
      if (((ht = !1), (t.pendingProps = r = i), (e.lanes & s) !== 0)) e.flags & 131072 && (ht = !0);
      else return ((t.lanes = e.lanes), Cn(e, t, s));
  }
  return eu(e, t, n, r, s);
}
function Yp(e, t, n) {
  var r = t.pendingProps,
    s = r.children,
    i = e !== null ? e.memoizedState : null;
  if (r.mode === 'hidden')
    if (!(t.mode & 1))
      ((t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }),
        we(us, vt),
        (vt |= n));
    else {
      if (!(n & 1073741824))
        return (
          (e = i !== null ? i.baseLanes | n : n),
          (t.lanes = t.childLanes = 1073741824),
          (t.memoizedState = { baseLanes: e, cachePool: null, transitions: null }),
          (t.updateQueue = null),
          we(us, vt),
          (vt |= e),
          null
        );
      ((t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }),
        (r = i !== null ? i.baseLanes : n),
        we(us, vt),
        (vt |= r));
    }
  else
    (i !== null ? ((r = i.baseLanes | n), (t.memoizedState = null)) : (r = n),
      we(us, vt),
      (vt |= r));
  return (rt(e, t, s, n), t.child);
}
function Xp(e, t) {
  var n = t.ref;
  ((e === null && n !== null) || (e !== null && e.ref !== n)) &&
    ((t.flags |= 512), (t.flags |= 2097152));
}
function eu(e, t, n, r, s) {
  var i = mt(n) ? Fr : et.current;
  return (
    (i = Ts(t, i)),
    ps(t, s),
    (n = vc(e, t, n, r, i, s)),
    (r = gc()),
    e !== null && !ht
      ? ((t.updateQueue = e.updateQueue), (t.flags &= -2053), (e.lanes &= ~s), Cn(e, t, s))
      : (Se && r && ic(t), (t.flags |= 1), rt(e, t, n, s), t.child)
  );
}
function Bd(e, t, n, r, s) {
  if (mt(n)) {
    var i = !0;
    ql(t);
  } else i = !1;
  if ((ps(t, s), t.stateNode === null)) (Ll(e, t), Hp(t, n, r), Xo(t, n, r, s), (r = !0));
  else if (e === null) {
    var l = t.stateNode,
      a = t.memoizedProps;
    l.props = a;
    var o = l.context,
      u = n.contextType;
    typeof u == 'object' && u !== null
      ? (u = At(u))
      : ((u = mt(n) ? Fr : et.current), (u = Ts(t, u)));
    var f = n.getDerivedStateFromProps,
      h = typeof f == 'function' || typeof l.getSnapshotBeforeUpdate == 'function';
    (h ||
      (typeof l.UNSAFE_componentWillReceiveProps != 'function' &&
        typeof l.componentWillReceiveProps != 'function') ||
      ((a !== r || o !== u) && Md(t, l, r, u)),
      (An = !1));
    var p = t.memoizedState;
    ((l.state = p),
      ea(t, r, l, s),
      (o = t.memoizedState),
      a !== r || p !== o || pt.current || An
        ? (typeof f == 'function' && (Yo(t, n, f, r), (o = t.memoizedState)),
          (a = An || Id(t, n, a, r, p, o, u))
            ? (h ||
                (typeof l.UNSAFE_componentWillMount != 'function' &&
                  typeof l.componentWillMount != 'function') ||
                (typeof l.componentWillMount == 'function' && l.componentWillMount(),
                typeof l.UNSAFE_componentWillMount == 'function' && l.UNSAFE_componentWillMount()),
              typeof l.componentDidMount == 'function' && (t.flags |= 4194308))
            : (typeof l.componentDidMount == 'function' && (t.flags |= 4194308),
              (t.memoizedProps = r),
              (t.memoizedState = o)),
          (l.props = r),
          (l.state = o),
          (l.context = u),
          (r = a))
        : (typeof l.componentDidMount == 'function' && (t.flags |= 4194308), (r = !1)));
  } else {
    ((l = t.stateNode),
      Np(e, t),
      (a = t.memoizedProps),
      (u = t.type === t.elementType ? a : Dt(t.type, a)),
      (l.props = u),
      (h = t.pendingProps),
      (p = l.context),
      (o = n.contextType),
      typeof o == 'object' && o !== null
        ? (o = At(o))
        : ((o = mt(n) ? Fr : et.current), (o = Ts(t, o))));
    var k = n.getDerivedStateFromProps;
    ((f = typeof k == 'function' || typeof l.getSnapshotBeforeUpdate == 'function') ||
      (typeof l.UNSAFE_componentWillReceiveProps != 'function' &&
        typeof l.componentWillReceiveProps != 'function') ||
      ((a !== h || p !== o) && Md(t, l, r, o)),
      (An = !1),
      (p = t.memoizedState),
      (l.state = p),
      ea(t, r, l, s));
    var S = t.memoizedState;
    a !== h || p !== S || pt.current || An
      ? (typeof k == 'function' && (Yo(t, n, k, r), (S = t.memoizedState)),
        (u = An || Id(t, n, u, r, p, S, o) || !1)
          ? (f ||
              (typeof l.UNSAFE_componentWillUpdate != 'function' &&
                typeof l.componentWillUpdate != 'function') ||
              (typeof l.componentWillUpdate == 'function' && l.componentWillUpdate(r, S, o),
              typeof l.UNSAFE_componentWillUpdate == 'function' &&
                l.UNSAFE_componentWillUpdate(r, S, o)),
            typeof l.componentDidUpdate == 'function' && (t.flags |= 4),
            typeof l.getSnapshotBeforeUpdate == 'function' && (t.flags |= 1024))
          : (typeof l.componentDidUpdate != 'function' ||
              (a === e.memoizedProps && p === e.memoizedState) ||
              (t.flags |= 4),
            typeof l.getSnapshotBeforeUpdate != 'function' ||
              (a === e.memoizedProps && p === e.memoizedState) ||
              (t.flags |= 1024),
            (t.memoizedProps = r),
            (t.memoizedState = S)),
        (l.props = r),
        (l.state = S),
        (l.context = o),
        (r = u))
      : (typeof l.componentDidUpdate != 'function' ||
          (a === e.memoizedProps && p === e.memoizedState) ||
          (t.flags |= 4),
        typeof l.getSnapshotBeforeUpdate != 'function' ||
          (a === e.memoizedProps && p === e.memoizedState) ||
          (t.flags |= 1024),
        (r = !1));
  }
  return tu(e, t, n, r, i, s);
}
function tu(e, t, n, r, s, i) {
  Xp(e, t);
  var l = (t.flags & 128) !== 0;
  if (!r && !l) return (s && Rd(t, n, !1), Cn(e, t, i));
  ((r = t.stateNode), (kg.current = t));
  var a = l && typeof n.getDerivedStateFromError != 'function' ? null : r.render();
  return (
    (t.flags |= 1),
    e !== null && l
      ? ((t.child = Ps(t, e.child, null, i)), (t.child = Ps(t, null, a, i)))
      : rt(e, t, a, i),
    (t.memoizedState = r.state),
    s && Rd(t, n, !0),
    t.child
  );
}
function Jp(e) {
  var t = e.stateNode;
  (t.pendingContext
    ? jd(e, t.pendingContext, t.pendingContext !== t.context)
    : t.context && jd(e, t.context, !1),
    hc(e, t.containerInfo));
}
function Qd(e, t, n, r, s) {
  return (Os(), ac(s), (t.flags |= 256), rt(e, t, n, r), t.child);
}
var nu = { dehydrated: null, treeContext: null, retryLane: 0 };
function ru(e) {
  return { baseLanes: e, cachePool: null, transitions: null };
}
function em(e, t, n) {
  var r = t.pendingProps,
    s = Ee.current,
    i = !1,
    l = (t.flags & 128) !== 0,
    a;
  if (
    ((a = l) || (a = e !== null && e.memoizedState === null ? !1 : (s & 2) !== 0),
    a ? ((i = !0), (t.flags &= -129)) : (e === null || e.memoizedState !== null) && (s |= 1),
    we(Ee, s & 1),
    e === null)
  )
    return (
      qo(t),
      (e = t.memoizedState),
      e !== null && ((e = e.dehydrated), e !== null)
        ? (t.mode & 1 ? (e.data === '$!' ? (t.lanes = 8) : (t.lanes = 1073741824)) : (t.lanes = 1),
          null)
        : ((l = r.children),
          (e = r.fallback),
          i
            ? ((r = t.mode),
              (i = t.child),
              (l = { mode: 'hidden', children: l }),
              !(r & 1) && i !== null
                ? ((i.childLanes = 0), (i.pendingProps = l))
                : (i = Pa(l, r, 0, null)),
              (e = Lr(e, r, n, null)),
              (i.return = t),
              (e.return = t),
              (i.sibling = e),
              (t.child = i),
              (t.child.memoizedState = ru(n)),
              (t.memoizedState = nu),
              e)
            : _c(t, l))
    );
  if (((s = e.memoizedState), s !== null && ((a = s.dehydrated), a !== null)))
    return Sg(e, t, l, r, a, s, n);
  if (i) {
    ((i = r.fallback), (l = t.mode), (s = e.child), (a = s.sibling));
    var o = { mode: 'hidden', children: r.children };
    return (
      !(l & 1) && t.child !== s
        ? ((r = t.child), (r.childLanes = 0), (r.pendingProps = o), (t.deletions = null))
        : ((r = sr(s, o)), (r.subtreeFlags = s.subtreeFlags & 14680064)),
      a !== null ? (i = sr(a, i)) : ((i = Lr(i, l, n, null)), (i.flags |= 2)),
      (i.return = t),
      (r.return = t),
      (r.sibling = i),
      (t.child = r),
      (r = i),
      (i = t.child),
      (l = e.child.memoizedState),
      (l =
        l === null
          ? ru(n)
          : { baseLanes: l.baseLanes | n, cachePool: null, transitions: l.transitions }),
      (i.memoizedState = l),
      (i.childLanes = e.childLanes & ~n),
      (t.memoizedState = nu),
      r
    );
  }
  return (
    (i = e.child),
    (e = i.sibling),
    (r = sr(i, { mode: 'visible', children: r.children })),
    !(t.mode & 1) && (r.lanes = n),
    (r.return = t),
    (r.sibling = null),
    e !== null &&
      ((n = t.deletions), n === null ? ((t.deletions = [e]), (t.flags |= 16)) : n.push(e)),
    (t.child = r),
    (t.memoizedState = null),
    r
  );
}
function _c(e, t) {
  return (
    (t = Pa({ mode: 'visible', children: t }, e.mode, 0, null)),
    (t.return = e),
    (e.child = t)
  );
}
function wl(e, t, n, r) {
  return (
    r !== null && ac(r),
    Ps(t, e.child, null, n),
    (e = _c(t, t.pendingProps.children)),
    (e.flags |= 2),
    (t.memoizedState = null),
    e
  );
}
function Sg(e, t, n, r, s, i, l) {
  if (n)
    return t.flags & 256
      ? ((t.flags &= -257), (r = ho(Error(R(422)))), wl(e, t, l, r))
      : t.memoizedState !== null
        ? ((t.child = e.child), (t.flags |= 128), null)
        : ((i = r.fallback),
          (s = t.mode),
          (r = Pa({ mode: 'visible', children: r.children }, s, 0, null)),
          (i = Lr(i, s, l, null)),
          (i.flags |= 2),
          (r.return = t),
          (i.return = t),
          (r.sibling = i),
          (t.child = r),
          t.mode & 1 && Ps(t, e.child, null, l),
          (t.child.memoizedState = ru(l)),
          (t.memoizedState = nu),
          i);
  if (!(t.mode & 1)) return wl(e, t, l, null);
  if (s.data === '$!') {
    if (((r = s.nextSibling && s.nextSibling.dataset), r)) var a = r.dgst;
    return ((r = a), (i = Error(R(419))), (r = ho(i, r, void 0)), wl(e, t, l, r));
  }
  if (((a = (l & e.childLanes) !== 0), ht || a)) {
    if (((r = We), r !== null)) {
      switch (l & -l) {
        case 4:
          s = 2;
          break;
        case 16:
          s = 8;
          break;
        case 64:
        case 128:
        case 256:
        case 512:
        case 1024:
        case 2048:
        case 4096:
        case 8192:
        case 16384:
        case 32768:
        case 65536:
        case 131072:
        case 262144:
        case 524288:
        case 1048576:
        case 2097152:
        case 4194304:
        case 8388608:
        case 16777216:
        case 33554432:
        case 67108864:
          s = 32;
          break;
        case 536870912:
          s = 268435456;
          break;
        default:
          s = 0;
      }
      ((s = s & (r.suspendedLanes | l) ? 0 : s),
        s !== 0 && s !== i.retryLane && ((i.retryLane = s), Sn(e, s), Zt(r, e, s, -1)));
    }
    return (jc(), (r = ho(Error(R(421)))), wl(e, t, l, r));
  }
  return s.data === '$?'
    ? ((t.flags |= 128), (t.child = e.child), (t = Ig.bind(null, e)), (s._reactRetry = t), null)
    : ((e = i.treeContext),
      (xt = er(s.nextSibling)),
      (wt = t),
      (Se = !0),
      ($t = null),
      e !== null &&
        ((Tt[Ot++] = vn),
        (Tt[Ot++] = gn),
        (Tt[Ot++] = Ir),
        (vn = e.id),
        (gn = e.overflow),
        (Ir = t)),
      (t = _c(t, r.children)),
      (t.flags |= 4096),
      t);
}
function Wd(e, t, n) {
  e.lanes |= t;
  var r = e.alternate;
  (r !== null && (r.lanes |= t), Go(e.return, t, n));
}
function po(e, t, n, r, s) {
  var i = e.memoizedState;
  i === null
    ? (e.memoizedState = {
        isBackwards: t,
        rendering: null,
        renderingStartTime: 0,
        last: r,
        tail: n,
        tailMode: s,
      })
    : ((i.isBackwards = t),
      (i.rendering = null),
      (i.renderingStartTime = 0),
      (i.last = r),
      (i.tail = n),
      (i.tailMode = s));
}
function tm(e, t, n) {
  var r = t.pendingProps,
    s = r.revealOrder,
    i = r.tail;
  if ((rt(e, t, r.children, n), (r = Ee.current), r & 2)) ((r = (r & 1) | 2), (t.flags |= 128));
  else {
    if (e !== null && e.flags & 128)
      e: for (e = t.child; e !== null; ) {
        if (e.tag === 13) e.memoizedState !== null && Wd(e, n, t);
        else if (e.tag === 19) Wd(e, n, t);
        else if (e.child !== null) {
          ((e.child.return = e), (e = e.child));
          continue;
        }
        if (e === t) break e;
        for (; e.sibling === null; ) {
          if (e.return === null || e.return === t) break e;
          e = e.return;
        }
        ((e.sibling.return = e.return), (e = e.sibling));
      }
    r &= 1;
  }
  if ((we(Ee, r), !(t.mode & 1))) t.memoizedState = null;
  else
    switch (s) {
      case 'forwards':
        for (n = t.child, s = null; n !== null; )
          ((e = n.alternate), e !== null && ta(e) === null && (s = n), (n = n.sibling));
        ((n = s),
          n === null ? ((s = t.child), (t.child = null)) : ((s = n.sibling), (n.sibling = null)),
          po(t, !1, s, n, i));
        break;
      case 'backwards':
        for (n = null, s = t.child, t.child = null; s !== null; ) {
          if (((e = s.alternate), e !== null && ta(e) === null)) {
            t.child = s;
            break;
          }
          ((e = s.sibling), (s.sibling = n), (n = s), (s = e));
        }
        po(t, !0, n, null, i);
        break;
      case 'together':
        po(t, !1, null, null, void 0);
        break;
      default:
        t.memoizedState = null;
    }
  return t.child;
}
function Ll(e, t) {
  !(t.mode & 1) && e !== null && ((e.alternate = null), (t.alternate = null), (t.flags |= 2));
}
function Cn(e, t, n) {
  if ((e !== null && (t.dependencies = e.dependencies), (Dr |= t.lanes), !(n & t.childLanes)))
    return null;
  if (e !== null && t.child !== e.child) throw Error(R(153));
  if (t.child !== null) {
    for (e = t.child, n = sr(e, e.pendingProps), t.child = n, n.return = t; e.sibling !== null; )
      ((e = e.sibling), (n = n.sibling = sr(e, e.pendingProps)), (n.return = t));
    n.sibling = null;
  }
  return t.child;
}
function Cg(e, t, n) {
  switch (t.tag) {
    case 3:
      (Jp(t), Os());
      break;
    case 5:
      jp(t);
      break;
    case 1:
      mt(t.type) && ql(t);
      break;
    case 4:
      hc(t, t.stateNode.containerInfo);
      break;
    case 10:
      var r = t.type._context,
        s = t.memoizedProps.value;
      (we(Xl, r._currentValue), (r._currentValue = s));
      break;
    case 13:
      if (((r = t.memoizedState), r !== null))
        return r.dehydrated !== null
          ? (we(Ee, Ee.current & 1), (t.flags |= 128), null)
          : n & t.child.childLanes
            ? em(e, t, n)
            : (we(Ee, Ee.current & 1), (e = Cn(e, t, n)), e !== null ? e.sibling : null);
      we(Ee, Ee.current & 1);
      break;
    case 19:
      if (((r = (n & t.childLanes) !== 0), e.flags & 128)) {
        if (r) return tm(e, t, n);
        t.flags |= 128;
      }
      if (
        ((s = t.memoizedState),
        s !== null && ((s.rendering = null), (s.tail = null), (s.lastEffect = null)),
        we(Ee, Ee.current),
        r)
      )
        break;
      return null;
    case 22:
    case 23:
      return ((t.lanes = 0), Yp(e, t, n));
  }
  return Cn(e, t, n);
}
var nm, su, rm, sm;
nm = function (e, t) {
  for (var n = t.child; n !== null; ) {
    if (n.tag === 5 || n.tag === 6) e.appendChild(n.stateNode);
    else if (n.tag !== 4 && n.child !== null) {
      ((n.child.return = n), (n = n.child));
      continue;
    }
    if (n === t) break;
    for (; n.sibling === null; ) {
      if (n.return === null || n.return === t) return;
      n = n.return;
    }
    ((n.sibling.return = n.return), (n = n.sibling));
  }
};
su = function () {};
rm = function (e, t, n, r) {
  var s = e.memoizedProps;
  if (s !== r) {
    ((e = t.stateNode), _r(sn.current));
    var i = null;
    switch (n) {
      case 'input':
        ((s = No(e, s)), (r = No(e, r)), (i = []));
        break;
      case 'select':
        ((s = je({}, s, { value: void 0 })), (r = je({}, r, { value: void 0 })), (i = []));
        break;
      case 'textarea':
        ((s = To(e, s)), (r = To(e, r)), (i = []));
        break;
      default:
        typeof s.onClick != 'function' && typeof r.onClick == 'function' && (e.onclick = Hl);
    }
    Po(n, r);
    var l;
    n = null;
    for (u in s)
      if (!r.hasOwnProperty(u) && s.hasOwnProperty(u) && s[u] != null)
        if (u === 'style') {
          var a = s[u];
          for (l in a) a.hasOwnProperty(l) && (n || (n = {}), (n[l] = ''));
        } else
          u !== 'dangerouslySetInnerHTML' &&
            u !== 'children' &&
            u !== 'suppressContentEditableWarning' &&
            u !== 'suppressHydrationWarning' &&
            u !== 'autoFocus' &&
            (ki.hasOwnProperty(u) ? i || (i = []) : (i = i || []).push(u, null));
    for (u in r) {
      var o = r[u];
      if (
        ((a = s != null ? s[u] : void 0),
        r.hasOwnProperty(u) && o !== a && (o != null || a != null))
      )
        if (u === 'style')
          if (a) {
            for (l in a)
              !a.hasOwnProperty(l) || (o && o.hasOwnProperty(l)) || (n || (n = {}), (n[l] = ''));
            for (l in o) o.hasOwnProperty(l) && a[l] !== o[l] && (n || (n = {}), (n[l] = o[l]));
          } else (n || (i || (i = []), i.push(u, n)), (n = o));
        else
          u === 'dangerouslySetInnerHTML'
            ? ((o = o ? o.__html : void 0),
              (a = a ? a.__html : void 0),
              o != null && a !== o && (i = i || []).push(u, o))
            : u === 'children'
              ? (typeof o != 'string' && typeof o != 'number') || (i = i || []).push(u, '' + o)
              : u !== 'suppressContentEditableWarning' &&
                u !== 'suppressHydrationWarning' &&
                (ki.hasOwnProperty(u)
                  ? (o != null && u === 'onScroll' && _e('scroll', e), i || a === o || (i = []))
                  : (i = i || []).push(u, o));
    }
    n && (i = i || []).push('style', n);
    var u = i;
    (t.updateQueue = u) && (t.flags |= 4);
  }
};
sm = function (e, t, n, r) {
  n !== r && (t.flags |= 4);
};
function ei(e, t) {
  if (!Se)
    switch (e.tailMode) {
      case 'hidden':
        t = e.tail;
        for (var n = null; t !== null; ) (t.alternate !== null && (n = t), (t = t.sibling));
        n === null ? (e.tail = null) : (n.sibling = null);
        break;
      case 'collapsed':
        n = e.tail;
        for (var r = null; n !== null; ) (n.alternate !== null && (r = n), (n = n.sibling));
        r === null
          ? t || e.tail === null
            ? (e.tail = null)
            : (e.tail.sibling = null)
          : (r.sibling = null);
    }
}
function Ye(e) {
  var t = e.alternate !== null && e.alternate.child === e.child,
    n = 0,
    r = 0;
  if (t)
    for (var s = e.child; s !== null; )
      ((n |= s.lanes | s.childLanes),
        (r |= s.subtreeFlags & 14680064),
        (r |= s.flags & 14680064),
        (s.return = e),
        (s = s.sibling));
  else
    for (s = e.child; s !== null; )
      ((n |= s.lanes | s.childLanes),
        (r |= s.subtreeFlags),
        (r |= s.flags),
        (s.return = e),
        (s = s.sibling));
  return ((e.subtreeFlags |= r), (e.childLanes = n), t);
}
function Eg(e, t, n) {
  var r = t.pendingProps;
  switch ((lc(t), t.tag)) {
    case 2:
    case 16:
    case 15:
    case 0:
    case 11:
    case 7:
    case 8:
    case 12:
    case 9:
    case 14:
      return (Ye(t), null);
    case 1:
      return (mt(t.type) && Kl(), Ye(t), null);
    case 3:
      return (
        (r = t.stateNode),
        bs(),
        ke(pt),
        ke(et),
        mc(),
        r.pendingContext && ((r.context = r.pendingContext), (r.pendingContext = null)),
        (e === null || e.child === null) &&
          (gl(t)
            ? (t.flags |= 4)
            : e === null ||
              (e.memoizedState.isDehydrated && !(t.flags & 256)) ||
              ((t.flags |= 1024), $t !== null && (fu($t), ($t = null)))),
        su(e, t),
        Ye(t),
        null
      );
    case 5:
      pc(t);
      var s = _r(Li.current);
      if (((n = t.type), e !== null && t.stateNode != null))
        (rm(e, t, n, r, s), e.ref !== t.ref && ((t.flags |= 512), (t.flags |= 2097152)));
      else {
        if (!r) {
          if (t.stateNode === null) throw Error(R(166));
          return (Ye(t), null);
        }
        if (((e = _r(sn.current)), gl(t))) {
          ((r = t.stateNode), (n = t.type));
          var i = t.memoizedProps;
          switch (((r[nn] = t), (r[bi] = i), (e = (t.mode & 1) !== 0), n)) {
            case 'dialog':
              (_e('cancel', r), _e('close', r));
              break;
            case 'iframe':
            case 'object':
            case 'embed':
              _e('load', r);
              break;
            case 'video':
            case 'audio':
              for (s = 0; s < ai.length; s++) _e(ai[s], r);
              break;
            case 'source':
              _e('error', r);
              break;
            case 'img':
            case 'image':
            case 'link':
              (_e('error', r), _e('load', r));
              break;
            case 'details':
              _e('toggle', r);
              break;
            case 'input':
              (ed(r, i), _e('invalid', r));
              break;
            case 'select':
              ((r._wrapperState = { wasMultiple: !!i.multiple }), _e('invalid', r));
              break;
            case 'textarea':
              (nd(r, i), _e('invalid', r));
          }
          (Po(n, i), (s = null));
          for (var l in i)
            if (i.hasOwnProperty(l)) {
              var a = i[l];
              l === 'children'
                ? typeof a == 'string'
                  ? r.textContent !== a &&
                    (i.suppressHydrationWarning !== !0 && vl(r.textContent, a, e),
                    (s = ['children', a]))
                  : typeof a == 'number' &&
                    r.textContent !== '' + a &&
                    (i.suppressHydrationWarning !== !0 && vl(r.textContent, a, e),
                    (s = ['children', '' + a]))
                : ki.hasOwnProperty(l) && a != null && l === 'onScroll' && _e('scroll', r);
            }
          switch (n) {
            case 'input':
              (ul(r), td(r, i, !0));
              break;
            case 'textarea':
              (ul(r), rd(r));
              break;
            case 'select':
            case 'option':
              break;
            default:
              typeof i.onClick == 'function' && (r.onclick = Hl);
          }
          ((r = s), (t.updateQueue = r), r !== null && (t.flags |= 4));
        } else {
          ((l = s.nodeType === 9 ? s : s.ownerDocument),
            e === 'http://www.w3.org/1999/xhtml' && (e = bh(n)),
            e === 'http://www.w3.org/1999/xhtml'
              ? n === 'script'
                ? ((e = l.createElement('div')),
                  (e.innerHTML = '<script><\/script>'),
                  (e = e.removeChild(e.firstChild)))
                : typeof r.is == 'string'
                  ? (e = l.createElement(n, { is: r.is }))
                  : ((e = l.createElement(n)),
                    n === 'select' &&
                      ((l = e), r.multiple ? (l.multiple = !0) : r.size && (l.size = r.size)))
              : (e = l.createElementNS(e, n)),
            (e[nn] = t),
            (e[bi] = r),
            nm(e, t, !1, !1),
            (t.stateNode = e));
          e: {
            switch (((l = bo(n, r)), n)) {
              case 'dialog':
                (_e('cancel', e), _e('close', e), (s = r));
                break;
              case 'iframe':
              case 'object':
              case 'embed':
                (_e('load', e), (s = r));
                break;
              case 'video':
              case 'audio':
                for (s = 0; s < ai.length; s++) _e(ai[s], e);
                s = r;
                break;
              case 'source':
                (_e('error', e), (s = r));
                break;
              case 'img':
              case 'image':
              case 'link':
                (_e('error', e), _e('load', e), (s = r));
                break;
              case 'details':
                (_e('toggle', e), (s = r));
                break;
              case 'input':
                (ed(e, r), (s = No(e, r)), _e('invalid', e));
                break;
              case 'option':
                s = r;
                break;
              case 'select':
                ((e._wrapperState = { wasMultiple: !!r.multiple }),
                  (s = je({}, r, { value: void 0 })),
                  _e('invalid', e));
                break;
              case 'textarea':
                (nd(e, r), (s = To(e, r)), _e('invalid', e));
                break;
              default:
                s = r;
            }
            (Po(n, s), (a = s));
            for (i in a)
              if (a.hasOwnProperty(i)) {
                var o = a[i];
                i === 'style'
                  ? Fh(e, o)
                  : i === 'dangerouslySetInnerHTML'
                    ? ((o = o ? o.__html : void 0), o != null && Ah(e, o))
                    : i === 'children'
                      ? typeof o == 'string'
                        ? (n !== 'textarea' || o !== '') && Si(e, o)
                        : typeof o == 'number' && Si(e, '' + o)
                      : i !== 'suppressContentEditableWarning' &&
                        i !== 'suppressHydrationWarning' &&
                        i !== 'autoFocus' &&
                        (ki.hasOwnProperty(i)
                          ? o != null && i === 'onScroll' && _e('scroll', e)
                          : o != null && Wu(e, i, o, l));
              }
            switch (n) {
              case 'input':
                (ul(e), td(e, r, !1));
                break;
              case 'textarea':
                (ul(e), rd(e));
                break;
              case 'option':
                r.value != null && e.setAttribute('value', '' + or(r.value));
                break;
              case 'select':
                ((e.multiple = !!r.multiple),
                  (i = r.value),
                  i != null
                    ? cs(e, !!r.multiple, i, !1)
                    : r.defaultValue != null && cs(e, !!r.multiple, r.defaultValue, !0));
                break;
              default:
                typeof s.onClick == 'function' && (e.onclick = Hl);
            }
            switch (n) {
              case 'button':
              case 'input':
              case 'select':
              case 'textarea':
                r = !!r.autoFocus;
                break e;
              case 'img':
                r = !0;
                break e;
              default:
                r = !1;
            }
          }
          r && (t.flags |= 4);
        }
        t.ref !== null && ((t.flags |= 512), (t.flags |= 2097152));
      }
      return (Ye(t), null);
    case 6:
      if (e && t.stateNode != null) sm(e, t, e.memoizedProps, r);
      else {
        if (typeof r != 'string' && t.stateNode === null) throw Error(R(166));
        if (((n = _r(Li.current)), _r(sn.current), gl(t))) {
          if (
            ((r = t.stateNode),
            (n = t.memoizedProps),
            (r[nn] = t),
            (i = r.nodeValue !== n) && ((e = wt), e !== null))
          )
            switch (e.tag) {
              case 3:
                vl(r.nodeValue, n, (e.mode & 1) !== 0);
                break;
              case 5:
                e.memoizedProps.suppressHydrationWarning !== !0 &&
                  vl(r.nodeValue, n, (e.mode & 1) !== 0);
            }
          i && (t.flags |= 4);
        } else
          ((r = (n.nodeType === 9 ? n : n.ownerDocument).createTextNode(r)),
            (r[nn] = t),
            (t.stateNode = r));
      }
      return (Ye(t), null);
    case 13:
      if (
        (ke(Ee),
        (r = t.memoizedState),
        e === null || (e.memoizedState !== null && e.memoizedState.dehydrated !== null))
      ) {
        if (Se && xt !== null && t.mode & 1 && !(t.flags & 128))
          (kp(), Os(), (t.flags |= 98560), (i = !1));
        else if (((i = gl(t)), r !== null && r.dehydrated !== null)) {
          if (e === null) {
            if (!i) throw Error(R(318));
            if (((i = t.memoizedState), (i = i !== null ? i.dehydrated : null), !i))
              throw Error(R(317));
            i[nn] = t;
          } else (Os(), !(t.flags & 128) && (t.memoizedState = null), (t.flags |= 4));
          (Ye(t), (i = !1));
        } else ($t !== null && (fu($t), ($t = null)), (i = !0));
        if (!i) return t.flags & 65536 ? t : null;
      }
      return t.flags & 128
        ? ((t.lanes = n), t)
        : ((r = r !== null),
          r !== (e !== null && e.memoizedState !== null) &&
            r &&
            ((t.child.flags |= 8192),
            t.mode & 1 && (e === null || Ee.current & 1 ? Ue === 0 && (Ue = 3) : jc())),
          t.updateQueue !== null && (t.flags |= 4),
          Ye(t),
          null);
    case 4:
      return (bs(), su(e, t), e === null && Oi(t.stateNode.containerInfo), Ye(t), null);
    case 10:
      return (cc(t.type._context), Ye(t), null);
    case 17:
      return (mt(t.type) && Kl(), Ye(t), null);
    case 19:
      if ((ke(Ee), (i = t.memoizedState), i === null)) return (Ye(t), null);
      if (((r = (t.flags & 128) !== 0), (l = i.rendering), l === null))
        if (r) ei(i, !1);
        else {
          if (Ue !== 0 || (e !== null && e.flags & 128))
            for (e = t.child; e !== null; ) {
              if (((l = ta(e)), l !== null)) {
                for (
                  t.flags |= 128,
                    ei(i, !1),
                    r = l.updateQueue,
                    r !== null && ((t.updateQueue = r), (t.flags |= 4)),
                    t.subtreeFlags = 0,
                    r = n,
                    n = t.child;
                  n !== null;

                )
                  ((i = n),
                    (e = r),
                    (i.flags &= 14680066),
                    (l = i.alternate),
                    l === null
                      ? ((i.childLanes = 0),
                        (i.lanes = e),
                        (i.child = null),
                        (i.subtreeFlags = 0),
                        (i.memoizedProps = null),
                        (i.memoizedState = null),
                        (i.updateQueue = null),
                        (i.dependencies = null),
                        (i.stateNode = null))
                      : ((i.childLanes = l.childLanes),
                        (i.lanes = l.lanes),
                        (i.child = l.child),
                        (i.subtreeFlags = 0),
                        (i.deletions = null),
                        (i.memoizedProps = l.memoizedProps),
                        (i.memoizedState = l.memoizedState),
                        (i.updateQueue = l.updateQueue),
                        (i.type = l.type),
                        (e = l.dependencies),
                        (i.dependencies =
                          e === null ? null : { lanes: e.lanes, firstContext: e.firstContext })),
                    (n = n.sibling));
                return (we(Ee, (Ee.current & 1) | 2), t.child);
              }
              e = e.sibling;
            }
          i.tail !== null &&
            be() > Ls &&
            ((t.flags |= 128), (r = !0), ei(i, !1), (t.lanes = 4194304));
        }
      else {
        if (!r)
          if (((e = ta(l)), e !== null)) {
            if (
              ((t.flags |= 128),
              (r = !0),
              (n = e.updateQueue),
              n !== null && ((t.updateQueue = n), (t.flags |= 4)),
              ei(i, !0),
              i.tail === null && i.tailMode === 'hidden' && !l.alternate && !Se)
            )
              return (Ye(t), null);
          } else
            2 * be() - i.renderingStartTime > Ls &&
              n !== 1073741824 &&
              ((t.flags |= 128), (r = !0), ei(i, !1), (t.lanes = 4194304));
        i.isBackwards
          ? ((l.sibling = t.child), (t.child = l))
          : ((n = i.last), n !== null ? (n.sibling = l) : (t.child = l), (i.last = l));
      }
      return i.tail !== null
        ? ((t = i.tail),
          (i.rendering = t),
          (i.tail = t.sibling),
          (i.renderingStartTime = be()),
          (t.sibling = null),
          (n = Ee.current),
          we(Ee, r ? (n & 1) | 2 : n & 1),
          t)
        : (Ye(t), null);
    case 22:
    case 23:
      return (
        Nc(),
        (r = t.memoizedState !== null),
        e !== null && (e.memoizedState !== null) !== r && (t.flags |= 8192),
        r && t.mode & 1
          ? vt & 1073741824 && (Ye(t), t.subtreeFlags & 6 && (t.flags |= 8192))
          : Ye(t),
        null
      );
    case 24:
      return null;
    case 25:
      return null;
  }
  throw Error(R(156, t.tag));
}
function Ng(e, t) {
  switch ((lc(t), t.tag)) {
    case 1:
      return (
        mt(t.type) && Kl(),
        (e = t.flags),
        e & 65536 ? ((t.flags = (e & -65537) | 128), t) : null
      );
    case 3:
      return (
        bs(),
        ke(pt),
        ke(et),
        mc(),
        (e = t.flags),
        e & 65536 && !(e & 128) ? ((t.flags = (e & -65537) | 128), t) : null
      );
    case 5:
      return (pc(t), null);
    case 13:
      if ((ke(Ee), (e = t.memoizedState), e !== null && e.dehydrated !== null)) {
        if (t.alternate === null) throw Error(R(340));
        Os();
      }
      return ((e = t.flags), e & 65536 ? ((t.flags = (e & -65537) | 128), t) : null);
    case 19:
      return (ke(Ee), null);
    case 4:
      return (bs(), null);
    case 10:
      return (cc(t.type._context), null);
    case 22:
    case 23:
      return (Nc(), null);
    case 24:
      return null;
    default:
      return null;
  }
}
var _l = !1,
  Je = !1,
  jg = typeof WeakSet == 'function' ? WeakSet : Set,
  V = null;
function os(e, t) {
  var n = e.ref;
  if (n !== null)
    if (typeof n == 'function')
      try {
        n(null);
      } catch (r) {
        Oe(e, t, r);
      }
    else n.current = null;
}
function iu(e, t, n) {
  try {
    n();
  } catch (r) {
    Oe(e, t, r);
  }
}
var Zd = !1;
function Rg(e, t) {
  if ((($o = Ql), (e = up()), sc(e))) {
    if ('selectionStart' in e) var n = { start: e.selectionStart, end: e.selectionEnd };
    else
      e: {
        n = ((n = e.ownerDocument) && n.defaultView) || window;
        var r = n.getSelection && n.getSelection();
        if (r && r.rangeCount !== 0) {
          n = r.anchorNode;
          var s = r.anchorOffset,
            i = r.focusNode;
          r = r.focusOffset;
          try {
            (n.nodeType, i.nodeType);
          } catch {
            n = null;
            break e;
          }
          var l = 0,
            a = -1,
            o = -1,
            u = 0,
            f = 0,
            h = e,
            p = null;
          t: for (;;) {
            for (
              var k;
              h !== n || (s !== 0 && h.nodeType !== 3) || (a = l + s),
                h !== i || (r !== 0 && h.nodeType !== 3) || (o = l + r),
                h.nodeType === 3 && (l += h.nodeValue.length),
                (k = h.firstChild) !== null;

            )
              ((p = h), (h = k));
            for (;;) {
              if (h === e) break t;
              if (
                (p === n && ++u === s && (a = l),
                p === i && ++f === r && (o = l),
                (k = h.nextSibling) !== null)
              )
                break;
              ((h = p), (p = h.parentNode));
            }
            h = k;
          }
          n = a === -1 || o === -1 ? null : { start: a, end: o };
        } else n = null;
      }
    n = n || { start: 0, end: 0 };
  } else n = null;
  for (Bo = { focusedElem: e, selectionRange: n }, Ql = !1, V = t; V !== null; )
    if (((t = V), (e = t.child), (t.subtreeFlags & 1028) !== 0 && e !== null))
      ((e.return = t), (V = e));
    else
      for (; V !== null; ) {
        t = V;
        try {
          var S = t.alternate;
          if (t.flags & 1024)
            switch (t.tag) {
              case 0:
              case 11:
              case 15:
                break;
              case 1:
                if (S !== null) {
                  var _ = S.memoizedProps,
                    N = S.memoizedState,
                    y = t.stateNode,
                    d = y.getSnapshotBeforeUpdate(t.elementType === t.type ? _ : Dt(t.type, _), N);
                  y.__reactInternalSnapshotBeforeUpdate = d;
                }
                break;
              case 3:
                var m = t.stateNode.containerInfo;
                m.nodeType === 1
                  ? (m.textContent = '')
                  : m.nodeType === 9 && m.documentElement && m.removeChild(m.documentElement);
                break;
              case 5:
              case 6:
              case 4:
              case 17:
                break;
              default:
                throw Error(R(163));
            }
        } catch (x) {
          Oe(t, t.return, x);
        }
        if (((e = t.sibling), e !== null)) {
          ((e.return = t.return), (V = e));
          break;
        }
        V = t.return;
      }
  return ((S = Zd), (Zd = !1), S);
}
function vi(e, t, n) {
  var r = t.updateQueue;
  if (((r = r !== null ? r.lastEffect : null), r !== null)) {
    var s = (r = r.next);
    do {
      if ((s.tag & e) === e) {
        var i = s.destroy;
        ((s.destroy = void 0), i !== void 0 && iu(t, n, i));
      }
      s = s.next;
    } while (s !== r);
  }
}
function Ta(e, t) {
  if (((t = t.updateQueue), (t = t !== null ? t.lastEffect : null), t !== null)) {
    var n = (t = t.next);
    do {
      if ((n.tag & e) === e) {
        var r = n.create;
        n.destroy = r();
      }
      n = n.next;
    } while (n !== t);
  }
}
function lu(e) {
  var t = e.ref;
  if (t !== null) {
    var n = e.stateNode;
    switch (e.tag) {
      case 5:
        e = n;
        break;
      default:
        e = n;
    }
    typeof t == 'function' ? t(e) : (t.current = e);
  }
}
function im(e) {
  var t = e.alternate;
  (t !== null && ((e.alternate = null), im(t)),
    (e.child = null),
    (e.deletions = null),
    (e.sibling = null),
    e.tag === 5 &&
      ((t = e.stateNode),
      t !== null && (delete t[nn], delete t[bi], delete t[Zo], delete t[cg], delete t[dg])),
    (e.stateNode = null),
    (e.return = null),
    (e.dependencies = null),
    (e.memoizedProps = null),
    (e.memoizedState = null),
    (e.pendingProps = null),
    (e.stateNode = null),
    (e.updateQueue = null));
}
function lm(e) {
  return e.tag === 5 || e.tag === 3 || e.tag === 4;
}
function Hd(e) {
  e: for (;;) {
    for (; e.sibling === null; ) {
      if (e.return === null || lm(e.return)) return null;
      e = e.return;
    }
    for (e.sibling.return = e.return, e = e.sibling; e.tag !== 5 && e.tag !== 6 && e.tag !== 18; ) {
      if (e.flags & 2 || e.child === null || e.tag === 4) continue e;
      ((e.child.return = e), (e = e.child));
    }
    if (!(e.flags & 2)) return e.stateNode;
  }
}
function au(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6)
    ((e = e.stateNode),
      t
        ? n.nodeType === 8
          ? n.parentNode.insertBefore(e, t)
          : n.insertBefore(e, t)
        : (n.nodeType === 8
            ? ((t = n.parentNode), t.insertBefore(e, n))
            : ((t = n), t.appendChild(e)),
          (n = n._reactRootContainer),
          n != null || t.onclick !== null || (t.onclick = Hl)));
  else if (r !== 4 && ((e = e.child), e !== null))
    for (au(e, t, n), e = e.sibling; e !== null; ) (au(e, t, n), (e = e.sibling));
}
function ou(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6) ((e = e.stateNode), t ? n.insertBefore(e, t) : n.appendChild(e));
  else if (r !== 4 && ((e = e.child), e !== null))
    for (ou(e, t, n), e = e.sibling; e !== null; ) (ou(e, t, n), (e = e.sibling));
}
var Ze = null,
  Vt = !1;
function Tn(e, t, n) {
  for (n = n.child; n !== null; ) (am(e, t, n), (n = n.sibling));
}
function am(e, t, n) {
  if (rn && typeof rn.onCommitFiberUnmount == 'function')
    try {
      rn.onCommitFiberUnmount(_a, n);
    } catch {}
  switch (n.tag) {
    case 5:
      Je || os(n, t);
    case 6:
      var r = Ze,
        s = Vt;
      ((Ze = null),
        Tn(e, t, n),
        (Ze = r),
        (Vt = s),
        Ze !== null &&
          (Vt
            ? ((e = Ze),
              (n = n.stateNode),
              e.nodeType === 8 ? e.parentNode.removeChild(n) : e.removeChild(n))
            : Ze.removeChild(n.stateNode)));
      break;
    case 18:
      Ze !== null &&
        (Vt
          ? ((e = Ze),
            (n = n.stateNode),
            e.nodeType === 8 ? lo(e.parentNode, n) : e.nodeType === 1 && lo(e, n),
            ji(e))
          : lo(Ze, n.stateNode));
      break;
    case 4:
      ((r = Ze),
        (s = Vt),
        (Ze = n.stateNode.containerInfo),
        (Vt = !0),
        Tn(e, t, n),
        (Ze = r),
        (Vt = s));
      break;
    case 0:
    case 11:
    case 14:
    case 15:
      if (!Je && ((r = n.updateQueue), r !== null && ((r = r.lastEffect), r !== null))) {
        s = r = r.next;
        do {
          var i = s,
            l = i.destroy;
          ((i = i.tag), l !== void 0 && (i & 2 || i & 4) && iu(n, t, l), (s = s.next));
        } while (s !== r);
      }
      Tn(e, t, n);
      break;
    case 1:
      if (!Je && (os(n, t), (r = n.stateNode), typeof r.componentWillUnmount == 'function'))
        try {
          ((r.props = n.memoizedProps), (r.state = n.memoizedState), r.componentWillUnmount());
        } catch (a) {
          Oe(n, t, a);
        }
      Tn(e, t, n);
      break;
    case 21:
      Tn(e, t, n);
      break;
    case 22:
      n.mode & 1
        ? ((Je = (r = Je) || n.memoizedState !== null), Tn(e, t, n), (Je = r))
        : Tn(e, t, n);
      break;
    default:
      Tn(e, t, n);
  }
}
function Kd(e) {
  var t = e.updateQueue;
  if (t !== null) {
    e.updateQueue = null;
    var n = e.stateNode;
    (n === null && (n = e.stateNode = new jg()),
      t.forEach(function (r) {
        var s = Mg.bind(null, e, r);
        n.has(r) || (n.add(r), r.then(s, s));
      }));
  }
}
function Mt(e, t) {
  var n = t.deletions;
  if (n !== null)
    for (var r = 0; r < n.length; r++) {
      var s = n[r];
      try {
        var i = e,
          l = t,
          a = l;
        e: for (; a !== null; ) {
          switch (a.tag) {
            case 5:
              ((Ze = a.stateNode), (Vt = !1));
              break e;
            case 3:
              ((Ze = a.stateNode.containerInfo), (Vt = !0));
              break e;
            case 4:
              ((Ze = a.stateNode.containerInfo), (Vt = !0));
              break e;
          }
          a = a.return;
        }
        if (Ze === null) throw Error(R(160));
        (am(i, l, s), (Ze = null), (Vt = !1));
        var o = s.alternate;
        (o !== null && (o.return = null), (s.return = null));
      } catch (u) {
        Oe(s, t, u);
      }
    }
  if (t.subtreeFlags & 12854) for (t = t.child; t !== null; ) (om(t, e), (t = t.sibling));
}
function om(e, t) {
  var n = e.alternate,
    r = e.flags;
  switch (e.tag) {
    case 0:
    case 11:
    case 14:
    case 15:
      if ((Mt(t, e), Gt(e), r & 4)) {
        try {
          (vi(3, e, e.return), Ta(3, e));
        } catch (_) {
          Oe(e, e.return, _);
        }
        try {
          vi(5, e, e.return);
        } catch (_) {
          Oe(e, e.return, _);
        }
      }
      break;
    case 1:
      (Mt(t, e), Gt(e), r & 512 && n !== null && os(n, n.return));
      break;
    case 5:
      if ((Mt(t, e), Gt(e), r & 512 && n !== null && os(n, n.return), e.flags & 32)) {
        var s = e.stateNode;
        try {
          Si(s, '');
        } catch (_) {
          Oe(e, e.return, _);
        }
      }
      if (r & 4 && ((s = e.stateNode), s != null)) {
        var i = e.memoizedProps,
          l = n !== null ? n.memoizedProps : i,
          a = e.type,
          o = e.updateQueue;
        if (((e.updateQueue = null), o !== null))
          try {
            (a === 'input' && i.type === 'radio' && i.name != null && Oh(s, i), bo(a, l));
            var u = bo(a, i);
            for (l = 0; l < o.length; l += 2) {
              var f = o[l],
                h = o[l + 1];
              f === 'style'
                ? Fh(s, h)
                : f === 'dangerouslySetInnerHTML'
                  ? Ah(s, h)
                  : f === 'children'
                    ? Si(s, h)
                    : Wu(s, f, h, u);
            }
            switch (a) {
              case 'input':
                jo(s, i);
                break;
              case 'textarea':
                Ph(s, i);
                break;
              case 'select':
                var p = s._wrapperState.wasMultiple;
                s._wrapperState.wasMultiple = !!i.multiple;
                var k = i.value;
                k != null
                  ? cs(s, !!i.multiple, k, !1)
                  : p !== !!i.multiple &&
                    (i.defaultValue != null
                      ? cs(s, !!i.multiple, i.defaultValue, !0)
                      : cs(s, !!i.multiple, i.multiple ? [] : '', !1));
            }
            s[bi] = i;
          } catch (_) {
            Oe(e, e.return, _);
          }
      }
      break;
    case 6:
      if ((Mt(t, e), Gt(e), r & 4)) {
        if (e.stateNode === null) throw Error(R(162));
        ((s = e.stateNode), (i = e.memoizedProps));
        try {
          s.nodeValue = i;
        } catch (_) {
          Oe(e, e.return, _);
        }
      }
      break;
    case 3:
      if ((Mt(t, e), Gt(e), r & 4 && n !== null && n.memoizedState.isDehydrated))
        try {
          ji(t.containerInfo);
        } catch (_) {
          Oe(e, e.return, _);
        }
      break;
    case 4:
      (Mt(t, e), Gt(e));
      break;
    case 13:
      (Mt(t, e),
        Gt(e),
        (s = e.child),
        s.flags & 8192 &&
          ((i = s.memoizedState !== null),
          (s.stateNode.isHidden = i),
          !i || (s.alternate !== null && s.alternate.memoizedState !== null) || (Cc = be())),
        r & 4 && Kd(e));
      break;
    case 22:
      if (
        ((f = n !== null && n.memoizedState !== null),
        e.mode & 1 ? ((Je = (u = Je) || f), Mt(t, e), (Je = u)) : Mt(t, e),
        Gt(e),
        r & 8192)
      ) {
        if (((u = e.memoizedState !== null), (e.stateNode.isHidden = u) && !f && e.mode & 1))
          for (V = e, f = e.child; f !== null; ) {
            for (h = V = f; V !== null; ) {
              switch (((p = V), (k = p.child), p.tag)) {
                case 0:
                case 11:
                case 14:
                case 15:
                  vi(4, p, p.return);
                  break;
                case 1:
                  os(p, p.return);
                  var S = p.stateNode;
                  if (typeof S.componentWillUnmount == 'function') {
                    ((r = p), (n = p.return));
                    try {
                      ((t = r),
                        (S.props = t.memoizedProps),
                        (S.state = t.memoizedState),
                        S.componentWillUnmount());
                    } catch (_) {
                      Oe(r, n, _);
                    }
                  }
                  break;
                case 5:
                  os(p, p.return);
                  break;
                case 22:
                  if (p.memoizedState !== null) {
                    Gd(h);
                    continue;
                  }
              }
              k !== null ? ((k.return = p), (V = k)) : Gd(h);
            }
            f = f.sibling;
          }
        e: for (f = null, h = e; ; ) {
          if (h.tag === 5) {
            if (f === null) {
              f = h;
              try {
                ((s = h.stateNode),
                  u
                    ? ((i = s.style),
                      typeof i.setProperty == 'function'
                        ? i.setProperty('display', 'none', 'important')
                        : (i.display = 'none'))
                    : ((a = h.stateNode),
                      (o = h.memoizedProps.style),
                      (l = o != null && o.hasOwnProperty('display') ? o.display : null),
                      (a.style.display = Lh('display', l))));
              } catch (_) {
                Oe(e, e.return, _);
              }
            }
          } else if (h.tag === 6) {
            if (f === null)
              try {
                h.stateNode.nodeValue = u ? '' : h.memoizedProps;
              } catch (_) {
                Oe(e, e.return, _);
              }
          } else if (
            ((h.tag !== 22 && h.tag !== 23) || h.memoizedState === null || h === e) &&
            h.child !== null
          ) {
            ((h.child.return = h), (h = h.child));
            continue;
          }
          if (h === e) break e;
          for (; h.sibling === null; ) {
            if (h.return === null || h.return === e) break e;
            (f === h && (f = null), (h = h.return));
          }
          (f === h && (f = null), (h.sibling.return = h.return), (h = h.sibling));
        }
      }
      break;
    case 19:
      (Mt(t, e), Gt(e), r & 4 && Kd(e));
      break;
    case 21:
      break;
    default:
      (Mt(t, e), Gt(e));
  }
}
function Gt(e) {
  var t = e.flags;
  if (t & 2) {
    try {
      e: {
        for (var n = e.return; n !== null; ) {
          if (lm(n)) {
            var r = n;
            break e;
          }
          n = n.return;
        }
        throw Error(R(160));
      }
      switch (r.tag) {
        case 5:
          var s = r.stateNode;
          r.flags & 32 && (Si(s, ''), (r.flags &= -33));
          var i = Hd(e);
          ou(e, i, s);
          break;
        case 3:
        case 4:
          var l = r.stateNode.containerInfo,
            a = Hd(e);
          au(e, a, l);
          break;
        default:
          throw Error(R(161));
      }
    } catch (o) {
      Oe(e, e.return, o);
    }
    e.flags &= -3;
  }
  t & 4096 && (e.flags &= -4097);
}
function Tg(e, t, n) {
  ((V = e), um(e));
}
function um(e, t, n) {
  for (var r = (e.mode & 1) !== 0; V !== null; ) {
    var s = V,
      i = s.child;
    if (s.tag === 22 && r) {
      var l = s.memoizedState !== null || _l;
      if (!l) {
        var a = s.alternate,
          o = (a !== null && a.memoizedState !== null) || Je;
        a = _l;
        var u = Je;
        if (((_l = l), (Je = o) && !u))
          for (V = s; V !== null; )
            ((l = V),
              (o = l.child),
              l.tag === 22 && l.memoizedState !== null
                ? Yd(s)
                : o !== null
                  ? ((o.return = l), (V = o))
                  : Yd(s));
        for (; i !== null; ) ((V = i), um(i), (i = i.sibling));
        ((V = s), (_l = a), (Je = u));
      }
      qd(e);
    } else s.subtreeFlags & 8772 && i !== null ? ((i.return = s), (V = i)) : qd(e);
  }
}
function qd(e) {
  for (; V !== null; ) {
    var t = V;
    if (t.flags & 8772) {
      var n = t.alternate;
      try {
        if (t.flags & 8772)
          switch (t.tag) {
            case 0:
            case 11:
            case 15:
              Je || Ta(5, t);
              break;
            case 1:
              var r = t.stateNode;
              if (t.flags & 4 && !Je)
                if (n === null) r.componentDidMount();
                else {
                  var s = t.elementType === t.type ? n.memoizedProps : Dt(t.type, n.memoizedProps);
                  r.componentDidUpdate(s, n.memoizedState, r.__reactInternalSnapshotBeforeUpdate);
                }
              var i = t.updateQueue;
              i !== null && Ad(t, i, r);
              break;
            case 3:
              var l = t.updateQueue;
              if (l !== null) {
                if (((n = null), t.child !== null))
                  switch (t.child.tag) {
                    case 5:
                      n = t.child.stateNode;
                      break;
                    case 1:
                      n = t.child.stateNode;
                  }
                Ad(t, l, n);
              }
              break;
            case 5:
              var a = t.stateNode;
              if (n === null && t.flags & 4) {
                n = a;
                var o = t.memoizedProps;
                switch (t.type) {
                  case 'button':
                  case 'input':
                  case 'select':
                  case 'textarea':
                    o.autoFocus && n.focus();
                    break;
                  case 'img':
                    o.src && (n.src = o.src);
                }
              }
              break;
            case 6:
              break;
            case 4:
              break;
            case 12:
              break;
            case 13:
              if (t.memoizedState === null) {
                var u = t.alternate;
                if (u !== null) {
                  var f = u.memoizedState;
                  if (f !== null) {
                    var h = f.dehydrated;
                    h !== null && ji(h);
                  }
                }
              }
              break;
            case 19:
            case 17:
            case 21:
            case 22:
            case 23:
            case 25:
              break;
            default:
              throw Error(R(163));
          }
        Je || (t.flags & 512 && lu(t));
      } catch (p) {
        Oe(t, t.return, p);
      }
    }
    if (t === e) {
      V = null;
      break;
    }
    if (((n = t.sibling), n !== null)) {
      ((n.return = t.return), (V = n));
      break;
    }
    V = t.return;
  }
}
function Gd(e) {
  for (; V !== null; ) {
    var t = V;
    if (t === e) {
      V = null;
      break;
    }
    var n = t.sibling;
    if (n !== null) {
      ((n.return = t.return), (V = n));
      break;
    }
    V = t.return;
  }
}
function Yd(e) {
  for (; V !== null; ) {
    var t = V;
    try {
      switch (t.tag) {
        case 0:
        case 11:
        case 15:
          var n = t.return;
          try {
            Ta(4, t);
          } catch (o) {
            Oe(t, n, o);
          }
          break;
        case 1:
          var r = t.stateNode;
          if (typeof r.componentDidMount == 'function') {
            var s = t.return;
            try {
              r.componentDidMount();
            } catch (o) {
              Oe(t, s, o);
            }
          }
          var i = t.return;
          try {
            lu(t);
          } catch (o) {
            Oe(t, i, o);
          }
          break;
        case 5:
          var l = t.return;
          try {
            lu(t);
          } catch (o) {
            Oe(t, l, o);
          }
      }
    } catch (o) {
      Oe(t, t.return, o);
    }
    if (t === e) {
      V = null;
      break;
    }
    var a = t.sibling;
    if (a !== null) {
      ((a.return = t.return), (V = a));
      break;
    }
    V = t.return;
  }
}
var Og = Math.ceil,
  sa = Nn.ReactCurrentDispatcher,
  kc = Nn.ReactCurrentOwner,
  bt = Nn.ReactCurrentBatchConfig,
  oe = 0,
  We = null,
  Ie = null,
  He = 0,
  vt = 0,
  us = hr(0),
  Ue = 0,
  Di = null,
  Dr = 0,
  Oa = 0,
  Sc = 0,
  gi = null,
  ft = null,
  Cc = 0,
  Ls = 1 / 0,
  dn = null,
  ia = !1,
  uu = null,
  nr = null,
  kl = !1,
  Kn = null,
  la = 0,
  xi = 0,
  cu = null,
  Fl = -1,
  Il = 0;
function lt() {
  return oe & 6 ? be() : Fl !== -1 ? Fl : (Fl = be());
}
function rr(e) {
  return e.mode & 1
    ? oe & 2 && He !== 0
      ? He & -He
      : hg.transition !== null
        ? (Il === 0 && (Il = Hh()), Il)
        : ((e = pe), e !== 0 || ((e = window.event), (e = e === void 0 ? 16 : ep(e.type))), e)
    : 1;
}
function Zt(e, t, n, r) {
  if (50 < xi) throw ((xi = 0), (cu = null), Error(R(185)));
  (Gi(e, n, r),
    (!(oe & 2) || e !== We) &&
      (e === We && (!(oe & 2) && (Oa |= n), Ue === 4 && In(e, He)),
      yt(e, r),
      n === 1 && oe === 0 && !(t.mode & 1) && ((Ls = be() + 500), Na && pr())));
}
function yt(e, t) {
  var n = e.callbackNode;
  hv(e, t);
  var r = Bl(e, e === We ? He : 0);
  if (r === 0) (n !== null && ld(n), (e.callbackNode = null), (e.callbackPriority = 0));
  else if (((t = r & -r), e.callbackPriority !== t)) {
    if ((n != null && ld(n), t === 1))
      (e.tag === 0 ? fg(Xd.bind(null, e)) : xp(Xd.bind(null, e)),
        og(function () {
          !(oe & 6) && pr();
        }),
        (n = null));
    else {
      switch (Kh(r)) {
        case 1:
          n = Gu;
          break;
        case 4:
          n = Wh;
          break;
        case 16:
          n = $l;
          break;
        case 536870912:
          n = Zh;
          break;
        default:
          n = $l;
      }
      n = vm(n, cm.bind(null, e));
    }
    ((e.callbackPriority = t), (e.callbackNode = n));
  }
}
function cm(e, t) {
  if (((Fl = -1), (Il = 0), oe & 6)) throw Error(R(327));
  var n = e.callbackNode;
  if (ms() && e.callbackNode !== n) return null;
  var r = Bl(e, e === We ? He : 0);
  if (r === 0) return null;
  if (r & 30 || r & e.expiredLanes || t) t = aa(e, r);
  else {
    t = r;
    var s = oe;
    oe |= 2;
    var i = fm();
    (We !== e || He !== t) && ((dn = null), (Ls = be() + 500), Ar(e, t));
    do
      try {
        Ag();
        break;
      } catch (a) {
        dm(e, a);
      }
    while (!0);
    (uc(), (sa.current = i), (oe = s), Ie !== null ? (t = 0) : ((We = null), (He = 0), (t = Ue)));
  }
  if (t !== 0) {
    if ((t === 2 && ((s = Mo(e)), s !== 0 && ((r = s), (t = du(e, s)))), t === 1))
      throw ((n = Di), Ar(e, 0), In(e, r), yt(e, be()), n);
    if (t === 6) In(e, r);
    else {
      if (
        ((s = e.current.alternate),
        !(r & 30) &&
          !Pg(s) &&
          ((t = aa(e, r)), t === 2 && ((i = Mo(e)), i !== 0 && ((r = i), (t = du(e, i)))), t === 1))
      )
        throw ((n = Di), Ar(e, 0), In(e, r), yt(e, be()), n);
      switch (((e.finishedWork = s), (e.finishedLanes = r), t)) {
        case 0:
        case 1:
          throw Error(R(345));
        case 2:
          gr(e, ft, dn);
          break;
        case 3:
          if ((In(e, r), (r & 130023424) === r && ((t = Cc + 500 - be()), 10 < t))) {
            if (Bl(e, 0) !== 0) break;
            if (((s = e.suspendedLanes), (s & r) !== r)) {
              (lt(), (e.pingedLanes |= e.suspendedLanes & s));
              break;
            }
            e.timeoutHandle = Wo(gr.bind(null, e, ft, dn), t);
            break;
          }
          gr(e, ft, dn);
          break;
        case 4:
          if ((In(e, r), (r & 4194240) === r)) break;
          for (t = e.eventTimes, s = -1; 0 < r; ) {
            var l = 31 - Wt(r);
            ((i = 1 << l), (l = t[l]), l > s && (s = l), (r &= ~i));
          }
          if (
            ((r = s),
            (r = be() - r),
            (r =
              (120 > r
                ? 120
                : 480 > r
                  ? 480
                  : 1080 > r
                    ? 1080
                    : 1920 > r
                      ? 1920
                      : 3e3 > r
                        ? 3e3
                        : 4320 > r
                          ? 4320
                          : 1960 * Og(r / 1960)) - r),
            10 < r)
          ) {
            e.timeoutHandle = Wo(gr.bind(null, e, ft, dn), r);
            break;
          }
          gr(e, ft, dn);
          break;
        case 5:
          gr(e, ft, dn);
          break;
        default:
          throw Error(R(329));
      }
    }
  }
  return (yt(e, be()), e.callbackNode === n ? cm.bind(null, e) : null);
}
function du(e, t) {
  var n = gi;
  return (
    e.current.memoizedState.isDehydrated && (Ar(e, t).flags |= 256),
    (e = aa(e, t)),
    e !== 2 && ((t = ft), (ft = n), t !== null && fu(t)),
    e
  );
}
function fu(e) {
  ft === null ? (ft = e) : ft.push.apply(ft, e);
}
function Pg(e) {
  for (var t = e; ; ) {
    if (t.flags & 16384) {
      var n = t.updateQueue;
      if (n !== null && ((n = n.stores), n !== null))
        for (var r = 0; r < n.length; r++) {
          var s = n[r],
            i = s.getSnapshot;
          s = s.value;
          try {
            if (!Ht(i(), s)) return !1;
          } catch {
            return !1;
          }
        }
    }
    if (((n = t.child), t.subtreeFlags & 16384 && n !== null)) ((n.return = t), (t = n));
    else {
      if (t === e) break;
      for (; t.sibling === null; ) {
        if (t.return === null || t.return === e) return !0;
        t = t.return;
      }
      ((t.sibling.return = t.return), (t = t.sibling));
    }
  }
  return !0;
}
function In(e, t) {
  for (
    t &= ~Sc, t &= ~Oa, e.suspendedLanes |= t, e.pingedLanes &= ~t, e = e.expirationTimes;
    0 < t;

  ) {
    var n = 31 - Wt(t),
      r = 1 << n;
    ((e[n] = -1), (t &= ~r));
  }
}
function Xd(e) {
  if (oe & 6) throw Error(R(327));
  ms();
  var t = Bl(e, 0);
  if (!(t & 1)) return (yt(e, be()), null);
  var n = aa(e, t);
  if (e.tag !== 0 && n === 2) {
    var r = Mo(e);
    r !== 0 && ((t = r), (n = du(e, r)));
  }
  if (n === 1) throw ((n = Di), Ar(e, 0), In(e, t), yt(e, be()), n);
  if (n === 6) throw Error(R(345));
  return (
    (e.finishedWork = e.current.alternate),
    (e.finishedLanes = t),
    gr(e, ft, dn),
    yt(e, be()),
    null
  );
}
function Ec(e, t) {
  var n = oe;
  oe |= 1;
  try {
    return e(t);
  } finally {
    ((oe = n), oe === 0 && ((Ls = be() + 500), Na && pr()));
  }
}
function zr(e) {
  Kn !== null && Kn.tag === 0 && !(oe & 6) && ms();
  var t = oe;
  oe |= 1;
  var n = bt.transition,
    r = pe;
  try {
    if (((bt.transition = null), (pe = 1), e)) return e();
  } finally {
    ((pe = r), (bt.transition = n), (oe = t), !(oe & 6) && pr());
  }
}
function Nc() {
  ((vt = us.current), ke(us));
}
function Ar(e, t) {
  ((e.finishedWork = null), (e.finishedLanes = 0));
  var n = e.timeoutHandle;
  if ((n !== -1 && ((e.timeoutHandle = -1), ag(n)), Ie !== null))
    for (n = Ie.return; n !== null; ) {
      var r = n;
      switch ((lc(r), r.tag)) {
        case 1:
          ((r = r.type.childContextTypes), r != null && Kl());
          break;
        case 3:
          (bs(), ke(pt), ke(et), mc());
          break;
        case 5:
          pc(r);
          break;
        case 4:
          bs();
          break;
        case 13:
          ke(Ee);
          break;
        case 19:
          ke(Ee);
          break;
        case 10:
          cc(r.type._context);
          break;
        case 22:
        case 23:
          Nc();
      }
      n = n.return;
    }
  if (
    ((We = e),
    (Ie = e = sr(e.current, null)),
    (He = vt = t),
    (Ue = 0),
    (Di = null),
    (Sc = Oa = Dr = 0),
    (ft = gi = null),
    wr !== null)
  ) {
    for (t = 0; t < wr.length; t++)
      if (((n = wr[t]), (r = n.interleaved), r !== null)) {
        n.interleaved = null;
        var s = r.next,
          i = n.pending;
        if (i !== null) {
          var l = i.next;
          ((i.next = s), (r.next = l));
        }
        n.pending = r;
      }
    wr = null;
  }
  return e;
}
function dm(e, t) {
  do {
    var n = Ie;
    try {
      if ((uc(), (bl.current = ra), na)) {
        for (var r = Ne.memoizedState; r !== null; ) {
          var s = r.queue;
          (s !== null && (s.pending = null), (r = r.next));
        }
        na = !1;
      }
      if (
        ((Mr = 0),
        (Qe = De = Ne = null),
        (yi = !1),
        (Fi = 0),
        (kc.current = null),
        n === null || n.return === null)
      ) {
        ((Ue = 1), (Di = t), (Ie = null));
        break;
      }
      e: {
        var i = e,
          l = n.return,
          a = n,
          o = t;
        if (
          ((t = He),
          (a.flags |= 32768),
          o !== null && typeof o == 'object' && typeof o.then == 'function')
        ) {
          var u = o,
            f = a,
            h = f.tag;
          if (!(f.mode & 1) && (h === 0 || h === 11 || h === 15)) {
            var p = f.alternate;
            p
              ? ((f.updateQueue = p.updateQueue),
                (f.memoizedState = p.memoizedState),
                (f.lanes = p.lanes))
              : ((f.updateQueue = null), (f.memoizedState = null));
          }
          var k = zd(l);
          if (k !== null) {
            ((k.flags &= -257), Ud(k, l, a, i, t), k.mode & 1 && Dd(i, u, t), (t = k), (o = u));
            var S = t.updateQueue;
            if (S === null) {
              var _ = new Set();
              (_.add(o), (t.updateQueue = _));
            } else S.add(o);
            break e;
          } else {
            if (!(t & 1)) {
              (Dd(i, u, t), jc());
              break e;
            }
            o = Error(R(426));
          }
        } else if (Se && a.mode & 1) {
          var N = zd(l);
          if (N !== null) {
            (!(N.flags & 65536) && (N.flags |= 256), Ud(N, l, a, i, t), ac(As(o, a)));
            break e;
          }
        }
        ((i = o = As(o, a)), Ue !== 4 && (Ue = 2), gi === null ? (gi = [i]) : gi.push(i), (i = l));
        do {
          switch (i.tag) {
            case 3:
              ((i.flags |= 65536), (t &= -t), (i.lanes |= t));
              var y = Kp(i, o, t);
              bd(i, y);
              break e;
            case 1:
              a = o;
              var d = i.type,
                m = i.stateNode;
              if (
                !(i.flags & 128) &&
                (typeof d.getDerivedStateFromError == 'function' ||
                  (m !== null &&
                    typeof m.componentDidCatch == 'function' &&
                    (nr === null || !nr.has(m))))
              ) {
                ((i.flags |= 65536), (t &= -t), (i.lanes |= t));
                var x = qp(i, a, t);
                bd(i, x);
                break e;
              }
          }
          i = i.return;
        } while (i !== null);
      }
      pm(n);
    } catch (j) {
      ((t = j), Ie === n && n !== null && (Ie = n = n.return));
      continue;
    }
    break;
  } while (!0);
}
function fm() {
  var e = sa.current;
  return ((sa.current = ra), e === null ? ra : e);
}
function jc() {
  ((Ue === 0 || Ue === 3 || Ue === 2) && (Ue = 4),
    We === null || (!(Dr & 268435455) && !(Oa & 268435455)) || In(We, He));
}
function aa(e, t) {
  var n = oe;
  oe |= 2;
  var r = fm();
  (We !== e || He !== t) && ((dn = null), Ar(e, t));
  do
    try {
      bg();
      break;
    } catch (s) {
      dm(e, s);
    }
  while (!0);
  if ((uc(), (oe = n), (sa.current = r), Ie !== null)) throw Error(R(261));
  return ((We = null), (He = 0), Ue);
}
function bg() {
  for (; Ie !== null; ) hm(Ie);
}
function Ag() {
  for (; Ie !== null && !sv(); ) hm(Ie);
}
function hm(e) {
  var t = ym(e.alternate, e, vt);
  ((e.memoizedProps = e.pendingProps), t === null ? pm(e) : (Ie = t), (kc.current = null));
}
function pm(e) {
  var t = e;
  do {
    var n = t.alternate;
    if (((e = t.return), t.flags & 32768)) {
      if (((n = Ng(n, t)), n !== null)) {
        ((n.flags &= 32767), (Ie = n));
        return;
      }
      if (e !== null) ((e.flags |= 32768), (e.subtreeFlags = 0), (e.deletions = null));
      else {
        ((Ue = 6), (Ie = null));
        return;
      }
    } else if (((n = Eg(n, t, vt)), n !== null)) {
      Ie = n;
      return;
    }
    if (((t = t.sibling), t !== null)) {
      Ie = t;
      return;
    }
    Ie = t = e;
  } while (t !== null);
  Ue === 0 && (Ue = 5);
}
function gr(e, t, n) {
  var r = pe,
    s = bt.transition;
  try {
    ((bt.transition = null), (pe = 1), Lg(e, t, n, r));
  } finally {
    ((bt.transition = s), (pe = r));
  }
  return null;
}
function Lg(e, t, n, r) {
  do ms();
  while (Kn !== null);
  if (oe & 6) throw Error(R(327));
  n = e.finishedWork;
  var s = e.finishedLanes;
  if (n === null) return null;
  if (((e.finishedWork = null), (e.finishedLanes = 0), n === e.current)) throw Error(R(177));
  ((e.callbackNode = null), (e.callbackPriority = 0));
  var i = n.lanes | n.childLanes;
  if (
    (pv(e, i),
    e === We && ((Ie = We = null), (He = 0)),
    (!(n.subtreeFlags & 2064) && !(n.flags & 2064)) ||
      kl ||
      ((kl = !0),
      vm($l, function () {
        return (ms(), null);
      })),
    (i = (n.flags & 15990) !== 0),
    n.subtreeFlags & 15990 || i)
  ) {
    ((i = bt.transition), (bt.transition = null));
    var l = pe;
    pe = 1;
    var a = oe;
    ((oe |= 4),
      (kc.current = null),
      Rg(e, n),
      om(n, e),
      eg(Bo),
      (Ql = !!$o),
      (Bo = $o = null),
      (e.current = n),
      Tg(n),
      iv(),
      (oe = a),
      (pe = l),
      (bt.transition = i));
  } else e.current = n;
  if (
    (kl && ((kl = !1), (Kn = e), (la = s)),
    (i = e.pendingLanes),
    i === 0 && (nr = null),
    ov(n.stateNode),
    yt(e, be()),
    t !== null)
  )
    for (r = e.onRecoverableError, n = 0; n < t.length; n++)
      ((s = t[n]), r(s.value, { componentStack: s.stack, digest: s.digest }));
  if (ia) throw ((ia = !1), (e = uu), (uu = null), e);
  return (
    la & 1 && e.tag !== 0 && ms(),
    (i = e.pendingLanes),
    i & 1 ? (e === cu ? xi++ : ((xi = 0), (cu = e))) : (xi = 0),
    pr(),
    null
  );
}
function ms() {
  if (Kn !== null) {
    var e = Kh(la),
      t = bt.transition,
      n = pe;
    try {
      if (((bt.transition = null), (pe = 16 > e ? 16 : e), Kn === null)) var r = !1;
      else {
        if (((e = Kn), (Kn = null), (la = 0), oe & 6)) throw Error(R(331));
        var s = oe;
        for (oe |= 4, V = e.current; V !== null; ) {
          var i = V,
            l = i.child;
          if (V.flags & 16) {
            var a = i.deletions;
            if (a !== null) {
              for (var o = 0; o < a.length; o++) {
                var u = a[o];
                for (V = u; V !== null; ) {
                  var f = V;
                  switch (f.tag) {
                    case 0:
                    case 11:
                    case 15:
                      vi(8, f, i);
                  }
                  var h = f.child;
                  if (h !== null) ((h.return = f), (V = h));
                  else
                    for (; V !== null; ) {
                      f = V;
                      var p = f.sibling,
                        k = f.return;
                      if ((im(f), f === u)) {
                        V = null;
                        break;
                      }
                      if (p !== null) {
                        ((p.return = k), (V = p));
                        break;
                      }
                      V = k;
                    }
                }
              }
              var S = i.alternate;
              if (S !== null) {
                var _ = S.child;
                if (_ !== null) {
                  S.child = null;
                  do {
                    var N = _.sibling;
                    ((_.sibling = null), (_ = N));
                  } while (_ !== null);
                }
              }
              V = i;
            }
          }
          if (i.subtreeFlags & 2064 && l !== null) ((l.return = i), (V = l));
          else
            e: for (; V !== null; ) {
              if (((i = V), i.flags & 2048))
                switch (i.tag) {
                  case 0:
                  case 11:
                  case 15:
                    vi(9, i, i.return);
                }
              var y = i.sibling;
              if (y !== null) {
                ((y.return = i.return), (V = y));
                break e;
              }
              V = i.return;
            }
        }
        var d = e.current;
        for (V = d; V !== null; ) {
          l = V;
          var m = l.child;
          if (l.subtreeFlags & 2064 && m !== null) ((m.return = l), (V = m));
          else
            e: for (l = d; V !== null; ) {
              if (((a = V), a.flags & 2048))
                try {
                  switch (a.tag) {
                    case 0:
                    case 11:
                    case 15:
                      Ta(9, a);
                  }
                } catch (j) {
                  Oe(a, a.return, j);
                }
              if (a === l) {
                V = null;
                break e;
              }
              var x = a.sibling;
              if (x !== null) {
                ((x.return = a.return), (V = x));
                break e;
              }
              V = a.return;
            }
        }
        if (((oe = s), pr(), rn && typeof rn.onPostCommitFiberRoot == 'function'))
          try {
            rn.onPostCommitFiberRoot(_a, e);
          } catch {}
        r = !0;
      }
      return r;
    } finally {
      ((pe = n), (bt.transition = t));
    }
  }
  return !1;
}
function Jd(e, t, n) {
  ((t = As(n, t)),
    (t = Kp(e, t, 1)),
    (e = tr(e, t, 1)),
    (t = lt()),
    e !== null && (Gi(e, 1, t), yt(e, t)));
}
function Oe(e, t, n) {
  if (e.tag === 3) Jd(e, e, n);
  else
    for (; t !== null; ) {
      if (t.tag === 3) {
        Jd(t, e, n);
        break;
      } else if (t.tag === 1) {
        var r = t.stateNode;
        if (
          typeof t.type.getDerivedStateFromError == 'function' ||
          (typeof r.componentDidCatch == 'function' && (nr === null || !nr.has(r)))
        ) {
          ((e = As(n, e)),
            (e = qp(t, e, 1)),
            (t = tr(t, e, 1)),
            (e = lt()),
            t !== null && (Gi(t, 1, e), yt(t, e)));
          break;
        }
      }
      t = t.return;
    }
}
function Fg(e, t, n) {
  var r = e.pingCache;
  (r !== null && r.delete(t),
    (t = lt()),
    (e.pingedLanes |= e.suspendedLanes & n),
    We === e &&
      (He & n) === n &&
      (Ue === 4 || (Ue === 3 && (He & 130023424) === He && 500 > be() - Cc) ? Ar(e, 0) : (Sc |= n)),
    yt(e, t));
}
function mm(e, t) {
  t === 0 && (e.mode & 1 ? ((t = fl), (fl <<= 1), !(fl & 130023424) && (fl = 4194304)) : (t = 1));
  var n = lt();
  ((e = Sn(e, t)), e !== null && (Gi(e, t, n), yt(e, n)));
}
function Ig(e) {
  var t = e.memoizedState,
    n = 0;
  (t !== null && (n = t.retryLane), mm(e, n));
}
function Mg(e, t) {
  var n = 0;
  switch (e.tag) {
    case 13:
      var r = e.stateNode,
        s = e.memoizedState;
      s !== null && (n = s.retryLane);
      break;
    case 19:
      r = e.stateNode;
      break;
    default:
      throw Error(R(314));
  }
  (r !== null && r.delete(t), mm(e, n));
}
var ym;
ym = function (e, t, n) {
  if (e !== null)
    if (e.memoizedProps !== t.pendingProps || pt.current) ht = !0;
    else {
      if (!(e.lanes & n) && !(t.flags & 128)) return ((ht = !1), Cg(e, t, n));
      ht = !!(e.flags & 131072);
    }
  else ((ht = !1), Se && t.flags & 1048576 && wp(t, Yl, t.index));
  switch (((t.lanes = 0), t.tag)) {
    case 2:
      var r = t.type;
      (Ll(e, t), (e = t.pendingProps));
      var s = Ts(t, et.current);
      (ps(t, n), (s = vc(null, t, r, e, s, n)));
      var i = gc();
      return (
        (t.flags |= 1),
        typeof s == 'object' && s !== null && typeof s.render == 'function' && s.$$typeof === void 0
          ? ((t.tag = 1),
            (t.memoizedState = null),
            (t.updateQueue = null),
            mt(r) ? ((i = !0), ql(t)) : (i = !1),
            (t.memoizedState = s.state !== null && s.state !== void 0 ? s.state : null),
            fc(t),
            (s.updater = Ra),
            (t.stateNode = s),
            (s._reactInternals = t),
            Xo(t, r, e, n),
            (t = tu(null, t, r, !0, i, n)))
          : ((t.tag = 0), Se && i && ic(t), rt(null, t, s, n), (t = t.child)),
        t
      );
    case 16:
      r = t.elementType;
      e: {
        switch (
          (Ll(e, t),
          (e = t.pendingProps),
          (s = r._init),
          (r = s(r._payload)),
          (t.type = r),
          (s = t.tag = zg(r)),
          (e = Dt(r, e)),
          s)
        ) {
          case 0:
            t = eu(null, t, r, e, n);
            break e;
          case 1:
            t = Bd(null, t, r, e, n);
            break e;
          case 11:
            t = Vd(null, t, r, e, n);
            break e;
          case 14:
            t = $d(null, t, r, Dt(r.type, e), n);
            break e;
        }
        throw Error(R(306, r, ''));
      }
      return t;
    case 0:
      return (
        (r = t.type),
        (s = t.pendingProps),
        (s = t.elementType === r ? s : Dt(r, s)),
        eu(e, t, r, s, n)
      );
    case 1:
      return (
        (r = t.type),
        (s = t.pendingProps),
        (s = t.elementType === r ? s : Dt(r, s)),
        Bd(e, t, r, s, n)
      );
    case 3:
      e: {
        if ((Jp(t), e === null)) throw Error(R(387));
        ((r = t.pendingProps), (i = t.memoizedState), (s = i.element), Np(e, t), ea(t, r, null, n));
        var l = t.memoizedState;
        if (((r = l.element), i.isDehydrated))
          if (
            ((i = {
              element: r,
              isDehydrated: !1,
              cache: l.cache,
              pendingSuspenseBoundaries: l.pendingSuspenseBoundaries,
              transitions: l.transitions,
            }),
            (t.updateQueue.baseState = i),
            (t.memoizedState = i),
            t.flags & 256)
          ) {
            ((s = As(Error(R(423)), t)), (t = Qd(e, t, r, n, s)));
            break e;
          } else if (r !== s) {
            ((s = As(Error(R(424)), t)), (t = Qd(e, t, r, n, s)));
            break e;
          } else
            for (
              xt = er(t.stateNode.containerInfo.firstChild),
                wt = t,
                Se = !0,
                $t = null,
                n = Cp(t, null, r, n),
                t.child = n;
              n;

            )
              ((n.flags = (n.flags & -3) | 4096), (n = n.sibling));
        else {
          if ((Os(), r === s)) {
            t = Cn(e, t, n);
            break e;
          }
          rt(e, t, r, n);
        }
        t = t.child;
      }
      return t;
    case 5:
      return (
        jp(t),
        e === null && qo(t),
        (r = t.type),
        (s = t.pendingProps),
        (i = e !== null ? e.memoizedProps : null),
        (l = s.children),
        Qo(r, s) ? (l = null) : i !== null && Qo(r, i) && (t.flags |= 32),
        Xp(e, t),
        rt(e, t, l, n),
        t.child
      );
    case 6:
      return (e === null && qo(t), null);
    case 13:
      return em(e, t, n);
    case 4:
      return (
        hc(t, t.stateNode.containerInfo),
        (r = t.pendingProps),
        e === null ? (t.child = Ps(t, null, r, n)) : rt(e, t, r, n),
        t.child
      );
    case 11:
      return (
        (r = t.type),
        (s = t.pendingProps),
        (s = t.elementType === r ? s : Dt(r, s)),
        Vd(e, t, r, s, n)
      );
    case 7:
      return (rt(e, t, t.pendingProps, n), t.child);
    case 8:
      return (rt(e, t, t.pendingProps.children, n), t.child);
    case 12:
      return (rt(e, t, t.pendingProps.children, n), t.child);
    case 10:
      e: {
        if (
          ((r = t.type._context),
          (s = t.pendingProps),
          (i = t.memoizedProps),
          (l = s.value),
          we(Xl, r._currentValue),
          (r._currentValue = l),
          i !== null)
        )
          if (Ht(i.value, l)) {
            if (i.children === s.children && !pt.current) {
              t = Cn(e, t, n);
              break e;
            }
          } else
            for (i = t.child, i !== null && (i.return = t); i !== null; ) {
              var a = i.dependencies;
              if (a !== null) {
                l = i.child;
                for (var o = a.firstContext; o !== null; ) {
                  if (o.context === r) {
                    if (i.tag === 1) {
                      ((o = xn(-1, n & -n)), (o.tag = 2));
                      var u = i.updateQueue;
                      if (u !== null) {
                        u = u.shared;
                        var f = u.pending;
                        (f === null ? (o.next = o) : ((o.next = f.next), (f.next = o)),
                          (u.pending = o));
                      }
                    }
                    ((i.lanes |= n),
                      (o = i.alternate),
                      o !== null && (o.lanes |= n),
                      Go(i.return, n, t),
                      (a.lanes |= n));
                    break;
                  }
                  o = o.next;
                }
              } else if (i.tag === 10) l = i.type === t.type ? null : i.child;
              else if (i.tag === 18) {
                if (((l = i.return), l === null)) throw Error(R(341));
                ((l.lanes |= n),
                  (a = l.alternate),
                  a !== null && (a.lanes |= n),
                  Go(l, n, t),
                  (l = i.sibling));
              } else l = i.child;
              if (l !== null) l.return = i;
              else
                for (l = i; l !== null; ) {
                  if (l === t) {
                    l = null;
                    break;
                  }
                  if (((i = l.sibling), i !== null)) {
                    ((i.return = l.return), (l = i));
                    break;
                  }
                  l = l.return;
                }
              i = l;
            }
        (rt(e, t, s.children, n), (t = t.child));
      }
      return t;
    case 9:
      return (
        (s = t.type),
        (r = t.pendingProps.children),
        ps(t, n),
        (s = At(s)),
        (r = r(s)),
        (t.flags |= 1),
        rt(e, t, r, n),
        t.child
      );
    case 14:
      return ((r = t.type), (s = Dt(r, t.pendingProps)), (s = Dt(r.type, s)), $d(e, t, r, s, n));
    case 15:
      return Gp(e, t, t.type, t.pendingProps, n);
    case 17:
      return (
        (r = t.type),
        (s = t.pendingProps),
        (s = t.elementType === r ? s : Dt(r, s)),
        Ll(e, t),
        (t.tag = 1),
        mt(r) ? ((e = !0), ql(t)) : (e = !1),
        ps(t, n),
        Hp(t, r, s),
        Xo(t, r, s, n),
        tu(null, t, r, !0, e, n)
      );
    case 19:
      return tm(e, t, n);
    case 22:
      return Yp(e, t, n);
  }
  throw Error(R(156, t.tag));
};
function vm(e, t) {
  return Qh(e, t);
}
function Dg(e, t, n, r) {
  ((this.tag = e),
    (this.key = n),
    (this.sibling =
      this.child =
      this.return =
      this.stateNode =
      this.type =
      this.elementType =
        null),
    (this.index = 0),
    (this.ref = null),
    (this.pendingProps = t),
    (this.dependencies = this.memoizedState = this.updateQueue = this.memoizedProps = null),
    (this.mode = r),
    (this.subtreeFlags = this.flags = 0),
    (this.deletions = null),
    (this.childLanes = this.lanes = 0),
    (this.alternate = null));
}
function Pt(e, t, n, r) {
  return new Dg(e, t, n, r);
}
function Rc(e) {
  return ((e = e.prototype), !(!e || !e.isReactComponent));
}
function zg(e) {
  if (typeof e == 'function') return Rc(e) ? 1 : 0;
  if (e != null) {
    if (((e = e.$$typeof), e === Hu)) return 11;
    if (e === Ku) return 14;
  }
  return 2;
}
function sr(e, t) {
  var n = e.alternate;
  return (
    n === null
      ? ((n = Pt(e.tag, t, e.key, e.mode)),
        (n.elementType = e.elementType),
        (n.type = e.type),
        (n.stateNode = e.stateNode),
        (n.alternate = e),
        (e.alternate = n))
      : ((n.pendingProps = t),
        (n.type = e.type),
        (n.flags = 0),
        (n.subtreeFlags = 0),
        (n.deletions = null)),
    (n.flags = e.flags & 14680064),
    (n.childLanes = e.childLanes),
    (n.lanes = e.lanes),
    (n.child = e.child),
    (n.memoizedProps = e.memoizedProps),
    (n.memoizedState = e.memoizedState),
    (n.updateQueue = e.updateQueue),
    (t = e.dependencies),
    (n.dependencies = t === null ? null : { lanes: t.lanes, firstContext: t.firstContext }),
    (n.sibling = e.sibling),
    (n.index = e.index),
    (n.ref = e.ref),
    n
  );
}
function Ml(e, t, n, r, s, i) {
  var l = 2;
  if (((r = e), typeof e == 'function')) Rc(e) && (l = 1);
  else if (typeof e == 'string') l = 5;
  else
    e: switch (e) {
      case Jr:
        return Lr(n.children, s, i, t);
      case Zu:
        ((l = 8), (s |= 8));
        break;
      case ko:
        return ((e = Pt(12, n, t, s | 2)), (e.elementType = ko), (e.lanes = i), e);
      case So:
        return ((e = Pt(13, n, t, s)), (e.elementType = So), (e.lanes = i), e);
      case Co:
        return ((e = Pt(19, n, t, s)), (e.elementType = Co), (e.lanes = i), e);
      case jh:
        return Pa(n, s, i, t);
      default:
        if (typeof e == 'object' && e !== null)
          switch (e.$$typeof) {
            case Eh:
              l = 10;
              break e;
            case Nh:
              l = 9;
              break e;
            case Hu:
              l = 11;
              break e;
            case Ku:
              l = 14;
              break e;
            case bn:
              ((l = 16), (r = null));
              break e;
          }
        throw Error(R(130, e == null ? e : typeof e, ''));
    }
  return ((t = Pt(l, n, t, s)), (t.elementType = e), (t.type = r), (t.lanes = i), t);
}
function Lr(e, t, n, r) {
  return ((e = Pt(7, e, r, t)), (e.lanes = n), e);
}
function Pa(e, t, n, r) {
  return (
    (e = Pt(22, e, r, t)),
    (e.elementType = jh),
    (e.lanes = n),
    (e.stateNode = { isHidden: !1 }),
    e
  );
}
function mo(e, t, n) {
  return ((e = Pt(6, e, null, t)), (e.lanes = n), e);
}
function yo(e, t, n) {
  return (
    (t = Pt(4, e.children !== null ? e.children : [], e.key, t)),
    (t.lanes = n),
    (t.stateNode = {
      containerInfo: e.containerInfo,
      pendingChildren: null,
      implementation: e.implementation,
    }),
    t
  );
}
function Ug(e, t, n, r, s) {
  ((this.tag = t),
    (this.containerInfo = e),
    (this.finishedWork = this.pingCache = this.current = this.pendingChildren = null),
    (this.timeoutHandle = -1),
    (this.callbackNode = this.pendingContext = this.context = null),
    (this.callbackPriority = 0),
    (this.eventTimes = qa(0)),
    (this.expirationTimes = qa(-1)),
    (this.entangledLanes =
      this.finishedLanes =
      this.mutableReadLanes =
      this.expiredLanes =
      this.pingedLanes =
      this.suspendedLanes =
      this.pendingLanes =
        0),
    (this.entanglements = qa(0)),
    (this.identifierPrefix = r),
    (this.onRecoverableError = s),
    (this.mutableSourceEagerHydrationData = null));
}
function Tc(e, t, n, r, s, i, l, a, o) {
  return (
    (e = new Ug(e, t, n, a, o)),
    t === 1 ? ((t = 1), i === !0 && (t |= 8)) : (t = 0),
    (i = Pt(3, null, null, t)),
    (e.current = i),
    (i.stateNode = e),
    (i.memoizedState = {
      element: r,
      isDehydrated: n,
      cache: null,
      transitions: null,
      pendingSuspenseBoundaries: null,
    }),
    fc(i),
    e
  );
}
function Vg(e, t, n) {
  var r = 3 < arguments.length && arguments[3] !== void 0 ? arguments[3] : null;
  return {
    $$typeof: Xr,
    key: r == null ? null : '' + r,
    children: e,
    containerInfo: t,
    implementation: n,
  };
}
function gm(e) {
  if (!e) return ur;
  e = e._reactInternals;
  e: {
    if (Qr(e) !== e || e.tag !== 1) throw Error(R(170));
    var t = e;
    do {
      switch (t.tag) {
        case 3:
          t = t.stateNode.context;
          break e;
        case 1:
          if (mt(t.type)) {
            t = t.stateNode.__reactInternalMemoizedMergedChildContext;
            break e;
          }
      }
      t = t.return;
    } while (t !== null);
    throw Error(R(171));
  }
  if (e.tag === 1) {
    var n = e.type;
    if (mt(n)) return gp(e, n, t);
  }
  return t;
}
function xm(e, t, n, r, s, i, l, a, o) {
  return (
    (e = Tc(n, r, !0, e, s, i, l, a, o)),
    (e.context = gm(null)),
    (n = e.current),
    (r = lt()),
    (s = rr(n)),
    (i = xn(r, s)),
    (i.callback = t ?? null),
    tr(n, i, s),
    (e.current.lanes = s),
    Gi(e, s, r),
    yt(e, r),
    e
  );
}
function ba(e, t, n, r) {
  var s = t.current,
    i = lt(),
    l = rr(s);
  return (
    (n = gm(n)),
    t.context === null ? (t.context = n) : (t.pendingContext = n),
    (t = xn(i, l)),
    (t.payload = { element: e }),
    (r = r === void 0 ? null : r),
    r !== null && (t.callback = r),
    (e = tr(s, t, l)),
    e !== null && (Zt(e, s, l, i), Pl(e, s, l)),
    l
  );
}
function oa(e) {
  if (((e = e.current), !e.child)) return null;
  switch (e.child.tag) {
    case 5:
      return e.child.stateNode;
    default:
      return e.child.stateNode;
  }
}
function ef(e, t) {
  if (((e = e.memoizedState), e !== null && e.dehydrated !== null)) {
    var n = e.retryLane;
    e.retryLane = n !== 0 && n < t ? n : t;
  }
}
function Oc(e, t) {
  (ef(e, t), (e = e.alternate) && ef(e, t));
}
function $g() {
  return null;
}
var wm =
  typeof reportError == 'function'
    ? reportError
    : function (e) {
        console.error(e);
      };
function Pc(e) {
  this._internalRoot = e;
}
Aa.prototype.render = Pc.prototype.render = function (e) {
  var t = this._internalRoot;
  if (t === null) throw Error(R(409));
  ba(e, t, null, null);
};
Aa.prototype.unmount = Pc.prototype.unmount = function () {
  var e = this._internalRoot;
  if (e !== null) {
    this._internalRoot = null;
    var t = e.containerInfo;
    (zr(function () {
      ba(null, e, null, null);
    }),
      (t[kn] = null));
  }
};
function Aa(e) {
  this._internalRoot = e;
}
Aa.prototype.unstable_scheduleHydration = function (e) {
  if (e) {
    var t = Yh();
    e = { blockedOn: null, target: e, priority: t };
    for (var n = 0; n < Fn.length && t !== 0 && t < Fn[n].priority; n++);
    (Fn.splice(n, 0, e), n === 0 && Jh(e));
  }
};
function bc(e) {
  return !(!e || (e.nodeType !== 1 && e.nodeType !== 9 && e.nodeType !== 11));
}
function La(e) {
  return !(
    !e ||
    (e.nodeType !== 1 &&
      e.nodeType !== 9 &&
      e.nodeType !== 11 &&
      (e.nodeType !== 8 || e.nodeValue !== ' react-mount-point-unstable '))
  );
}
function tf() {}
function Bg(e, t, n, r, s) {
  if (s) {
    if (typeof r == 'function') {
      var i = r;
      r = function () {
        var u = oa(l);
        i.call(u);
      };
    }
    var l = xm(t, r, e, 0, null, !1, !1, '', tf);
    return (
      (e._reactRootContainer = l),
      (e[kn] = l.current),
      Oi(e.nodeType === 8 ? e.parentNode : e),
      zr(),
      l
    );
  }
  for (; (s = e.lastChild); ) e.removeChild(s);
  if (typeof r == 'function') {
    var a = r;
    r = function () {
      var u = oa(o);
      a.call(u);
    };
  }
  var o = Tc(e, 0, !1, null, null, !1, !1, '', tf);
  return (
    (e._reactRootContainer = o),
    (e[kn] = o.current),
    Oi(e.nodeType === 8 ? e.parentNode : e),
    zr(function () {
      ba(t, o, n, r);
    }),
    o
  );
}
function Fa(e, t, n, r, s) {
  var i = n._reactRootContainer;
  if (i) {
    var l = i;
    if (typeof s == 'function') {
      var a = s;
      s = function () {
        var o = oa(l);
        a.call(o);
      };
    }
    ba(t, l, e, s);
  } else l = Bg(n, t, e, s, r);
  return oa(l);
}
qh = function (e) {
  switch (e.tag) {
    case 3:
      var t = e.stateNode;
      if (t.current.memoizedState.isDehydrated) {
        var n = li(t.pendingLanes);
        n !== 0 && (Yu(t, n | 1), yt(t, be()), !(oe & 6) && ((Ls = be() + 500), pr()));
      }
      break;
    case 13:
      (zr(function () {
        var r = Sn(e, 1);
        if (r !== null) {
          var s = lt();
          Zt(r, e, 1, s);
        }
      }),
        Oc(e, 1));
  }
};
Xu = function (e) {
  if (e.tag === 13) {
    var t = Sn(e, 134217728);
    if (t !== null) {
      var n = lt();
      Zt(t, e, 134217728, n);
    }
    Oc(e, 134217728);
  }
};
Gh = function (e) {
  if (e.tag === 13) {
    var t = rr(e),
      n = Sn(e, t);
    if (n !== null) {
      var r = lt();
      Zt(n, e, t, r);
    }
    Oc(e, t);
  }
};
Yh = function () {
  return pe;
};
Xh = function (e, t) {
  var n = pe;
  try {
    return ((pe = e), t());
  } finally {
    pe = n;
  }
};
Lo = function (e, t, n) {
  switch (t) {
    case 'input':
      if ((jo(e, n), (t = n.name), n.type === 'radio' && t != null)) {
        for (n = e; n.parentNode; ) n = n.parentNode;
        for (
          n = n.querySelectorAll('input[name=' + JSON.stringify('' + t) + '][type="radio"]'), t = 0;
          t < n.length;
          t++
        ) {
          var r = n[t];
          if (r !== e && r.form === e.form) {
            var s = Ea(r);
            if (!s) throw Error(R(90));
            (Th(r), jo(r, s));
          }
        }
      }
      break;
    case 'textarea':
      Ph(e, n);
      break;
    case 'select':
      ((t = n.value), t != null && cs(e, !!n.multiple, t, !1));
  }
};
Dh = Ec;
zh = zr;
var Qg = { usingClientEntryPoint: !1, Events: [Xi, rs, Ea, Ih, Mh, Ec] },
  ti = {
    findFiberByHostInstance: xr,
    bundleType: 0,
    version: '18.3.1',
    rendererPackageName: 'react-dom',
  },
  Wg = {
    bundleType: ti.bundleType,
    version: ti.version,
    rendererPackageName: ti.rendererPackageName,
    rendererConfig: ti.rendererConfig,
    overrideHookState: null,
    overrideHookStateDeletePath: null,
    overrideHookStateRenamePath: null,
    overrideProps: null,
    overridePropsDeletePath: null,
    overridePropsRenamePath: null,
    setErrorHandler: null,
    setSuspenseHandler: null,
    scheduleUpdate: null,
    currentDispatcherRef: Nn.ReactCurrentDispatcher,
    findHostInstanceByFiber: function (e) {
      return ((e = $h(e)), e === null ? null : e.stateNode);
    },
    findFiberByHostInstance: ti.findFiberByHostInstance || $g,
    findHostInstancesForRefresh: null,
    scheduleRefresh: null,
    scheduleRoot: null,
    setRefreshHandler: null,
    getCurrentFiber: null,
    reconcilerVersion: '18.3.1-next-f1338f8080-20240426',
  };
if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < 'u') {
  var Sl = __REACT_DEVTOOLS_GLOBAL_HOOK__;
  if (!Sl.isDisabled && Sl.supportsFiber)
    try {
      ((_a = Sl.inject(Wg)), (rn = Sl));
    } catch {}
}
St.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = Qg;
St.createPortal = function (e, t) {
  var n = 2 < arguments.length && arguments[2] !== void 0 ? arguments[2] : null;
  if (!bc(t)) throw Error(R(200));
  return Vg(e, t, null, n);
};
St.createRoot = function (e, t) {
  if (!bc(e)) throw Error(R(299));
  var n = !1,
    r = '',
    s = wm;
  return (
    t != null &&
      (t.unstable_strictMode === !0 && (n = !0),
      t.identifierPrefix !== void 0 && (r = t.identifierPrefix),
      t.onRecoverableError !== void 0 && (s = t.onRecoverableError)),
    (t = Tc(e, 1, !1, null, null, n, !1, r, s)),
    (e[kn] = t.current),
    Oi(e.nodeType === 8 ? e.parentNode : e),
    new Pc(t)
  );
};
St.findDOMNode = function (e) {
  if (e == null) return null;
  if (e.nodeType === 1) return e;
  var t = e._reactInternals;
  if (t === void 0)
    throw typeof e.render == 'function'
      ? Error(R(188))
      : ((e = Object.keys(e).join(',')), Error(R(268, e)));
  return ((e = $h(t)), (e = e === null ? null : e.stateNode), e);
};
St.flushSync = function (e) {
  return zr(e);
};
St.hydrate = function (e, t, n) {
  if (!La(t)) throw Error(R(200));
  return Fa(null, e, t, !0, n);
};
St.hydrateRoot = function (e, t, n) {
  if (!bc(e)) throw Error(R(405));
  var r = (n != null && n.hydratedSources) || null,
    s = !1,
    i = '',
    l = wm;
  if (
    (n != null &&
      (n.unstable_strictMode === !0 && (s = !0),
      n.identifierPrefix !== void 0 && (i = n.identifierPrefix),
      n.onRecoverableError !== void 0 && (l = n.onRecoverableError)),
    (t = xm(t, null, e, 1, n ?? null, s, !1, i, l)),
    (e[kn] = t.current),
    Oi(e),
    r)
  )
    for (e = 0; e < r.length; e++)
      ((n = r[e]),
        (s = n._getVersion),
        (s = s(n._source)),
        t.mutableSourceEagerHydrationData == null
          ? (t.mutableSourceEagerHydrationData = [n, s])
          : t.mutableSourceEagerHydrationData.push(n, s));
  return new Aa(t);
};
St.render = function (e, t, n) {
  if (!La(t)) throw Error(R(200));
  return Fa(null, e, t, !1, n);
};
St.unmountComponentAtNode = function (e) {
  if (!La(e)) throw Error(R(40));
  return e._reactRootContainer
    ? (zr(function () {
        Fa(null, null, e, !1, function () {
          ((e._reactRootContainer = null), (e[kn] = null));
        });
      }),
      !0)
    : !1;
};
St.unstable_batchedUpdates = Ec;
St.unstable_renderSubtreeIntoContainer = function (e, t, n, r) {
  if (!La(n)) throw Error(R(200));
  if (e == null || e._reactInternals === void 0) throw Error(R(38));
  return Fa(e, t, n, !1, r);
};
St.version = '18.3.1-next-f1338f8080-20240426';
function _m() {
  if (
    !(
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > 'u' ||
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE != 'function'
    )
  )
    try {
      __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(_m);
    } catch (e) {
      console.error(e);
    }
}
(_m(), (_h.exports = St));
var Zg = _h.exports,
  nf = Zg;
((wo.createRoot = nf.createRoot), (wo.hydrateRoot = nf.hydrateRoot));
var Qs = class {
    constructor() {
      ((this.listeners = new Set()), (this.subscribe = this.subscribe.bind(this)));
    }
    subscribe(e) {
      return (
        this.listeners.add(e),
        this.onSubscribe(),
        () => {
          (this.listeners.delete(e), this.onUnsubscribe());
        }
      );
    }
    hasListeners() {
      return this.listeners.size > 0;
    }
    onSubscribe() {}
    onUnsubscribe() {}
  },
  Hg = {
    setTimeout: (e, t) => setTimeout(e, t),
    clearTimeout: (e) => clearTimeout(e),
    setInterval: (e, t) => setInterval(e, t),
    clearInterval: (e) => clearInterval(e),
  },
  Dn,
  Du,
  Jf,
  Kg =
    ((Jf = class {
      constructor() {
        W(this, Dn, Hg);
        W(this, Du, !1);
      }
      setTimeoutProvider(e) {
        M(this, Dn, e);
      }
      setTimeout(e, t) {
        return v(this, Dn).setTimeout(e, t);
      }
      clearTimeout(e) {
        v(this, Dn).clearTimeout(e);
      }
      setInterval(e, t) {
        return v(this, Dn).setInterval(e, t);
      }
      clearInterval(e) {
        v(this, Dn).clearInterval(e);
      }
    }),
    (Dn = new WeakMap()),
    (Du = new WeakMap()),
    Jf),
  kr = new Kg();
function qg(e) {
  setTimeout(e, 0);
}
var Ur = typeof window > 'u' || 'Deno' in globalThis;
function st() {}
function Gg(e, t) {
  return typeof e == 'function' ? e(t) : e;
}
function hu(e) {
  return typeof e == 'number' && e >= 0 && e !== 1 / 0;
}
function km(e, t) {
  return Math.max(e + (t || 0) - Date.now(), 0);
}
function ir(e, t) {
  return typeof e == 'function' ? e(t) : e;
}
function Rt(e, t) {
  return typeof e == 'function' ? e(t) : e;
}
function rf(e, t) {
  const { type: n = 'all', exact: r, fetchStatus: s, predicate: i, queryKey: l, stale: a } = e;
  if (l) {
    if (r) {
      if (t.queryHash !== Ac(l, t.options)) return !1;
    } else if (!zi(t.queryKey, l)) return !1;
  }
  if (n !== 'all') {
    const o = t.isActive();
    if ((n === 'active' && !o) || (n === 'inactive' && o)) return !1;
  }
  return !(
    (typeof a == 'boolean' && t.isStale() !== a) ||
    (s && s !== t.state.fetchStatus) ||
    (i && !i(t))
  );
}
function sf(e, t) {
  const { exact: n, status: r, predicate: s, mutationKey: i } = e;
  if (i) {
    if (!t.options.mutationKey) return !1;
    if (n) {
      if (Vr(t.options.mutationKey) !== Vr(i)) return !1;
    } else if (!zi(t.options.mutationKey, i)) return !1;
  }
  return !((r && t.state.status !== r) || (s && !s(t)));
}
function Ac(e, t) {
  return ((t == null ? void 0 : t.queryKeyHashFn) || Vr)(e);
}
function Vr(e) {
  return JSON.stringify(e, (t, n) =>
    pu(n)
      ? Object.keys(n)
          .sort()
          .reduce((r, s) => ((r[s] = n[s]), r), {})
      : n,
  );
}
function zi(e, t) {
  return e === t
    ? !0
    : typeof e != typeof t
      ? !1
      : e && t && typeof e == 'object' && typeof t == 'object'
        ? Object.keys(t).every((n) => zi(e[n], t[n]))
        : !1;
}
var Yg = Object.prototype.hasOwnProperty;
function Sm(e, t) {
  if (e === t) return e;
  const n = lf(e) && lf(t);
  if (!n && !(pu(e) && pu(t))) return t;
  const s = (n ? e : Object.keys(e)).length,
    i = n ? t : Object.keys(t),
    l = i.length,
    a = n ? new Array(l) : {};
  let o = 0;
  for (let u = 0; u < l; u++) {
    const f = n ? u : i[u],
      h = e[f],
      p = t[f];
    if (h === p) {
      ((a[f] = h), (n ? u < s : Yg.call(e, f)) && o++);
      continue;
    }
    if (h === null || p === null || typeof h != 'object' || typeof p != 'object') {
      a[f] = p;
      continue;
    }
    const k = Sm(h, p);
    ((a[f] = k), k === h && o++);
  }
  return s === l && o === s ? e : a;
}
function ua(e, t) {
  if (!t || Object.keys(e).length !== Object.keys(t).length) return !1;
  for (const n in e) if (e[n] !== t[n]) return !1;
  return !0;
}
function lf(e) {
  return Array.isArray(e) && e.length === Object.keys(e).length;
}
function pu(e) {
  if (!af(e)) return !1;
  const t = e.constructor;
  if (t === void 0) return !0;
  const n = t.prototype;
  return !(
    !af(n) ||
    !n.hasOwnProperty('isPrototypeOf') ||
    Object.getPrototypeOf(e) !== Object.prototype
  );
}
function af(e) {
  return Object.prototype.toString.call(e) === '[object Object]';
}
function Xg(e) {
  return new Promise((t) => {
    kr.setTimeout(t, e);
  });
}
function mu(e, t, n) {
  return typeof n.structuralSharing == 'function'
    ? n.structuralSharing(e, t)
    : n.structuralSharing !== !1
      ? Sm(e, t)
      : t;
}
function Jg(e, t, n = 0) {
  const r = [...e, t];
  return n && r.length > n ? r.slice(1) : r;
}
function e0(e, t, n = 0) {
  const r = [t, ...e];
  return n && r.length > n ? r.slice(0, -1) : r;
}
var Lc = Symbol();
function Cm(e, t) {
  return !e.queryFn && t != null && t.initialPromise
    ? () => t.initialPromise
    : !e.queryFn || e.queryFn === Lc
      ? () => Promise.reject(new Error(`Missing queryFn: '${e.queryHash}'`))
      : e.queryFn;
}
function Em(e, t) {
  return typeof e == 'function' ? e(...t) : !!e;
}
var Cr,
  zn,
  ys,
  eh,
  t0 =
    ((eh = class extends Qs {
      constructor() {
        super();
        W(this, Cr);
        W(this, zn);
        W(this, ys);
        M(this, ys, (t) => {
          if (!Ur && window.addEventListener) {
            const n = () => t();
            return (
              window.addEventListener('visibilitychange', n, !1),
              () => {
                window.removeEventListener('visibilitychange', n);
              }
            );
          }
        });
      }
      onSubscribe() {
        v(this, zn) || this.setEventListener(v(this, ys));
      }
      onUnsubscribe() {
        var t;
        this.hasListeners() || ((t = v(this, zn)) == null || t.call(this), M(this, zn, void 0));
      }
      setEventListener(t) {
        var n;
        (M(this, ys, t),
          (n = v(this, zn)) == null || n.call(this),
          M(
            this,
            zn,
            t((r) => {
              typeof r == 'boolean' ? this.setFocused(r) : this.onFocus();
            }),
          ));
      }
      setFocused(t) {
        v(this, Cr) !== t && (M(this, Cr, t), this.onFocus());
      }
      onFocus() {
        const t = this.isFocused();
        this.listeners.forEach((n) => {
          n(t);
        });
      }
      isFocused() {
        var t;
        return typeof v(this, Cr) == 'boolean'
          ? v(this, Cr)
          : ((t = globalThis.document) == null ? void 0 : t.visibilityState) !== 'hidden';
      }
    }),
    (Cr = new WeakMap()),
    (zn = new WeakMap()),
    (ys = new WeakMap()),
    eh),
  Fc = new t0();
function yu() {
  let e, t;
  const n = new Promise((s, i) => {
    ((e = s), (t = i));
  });
  ((n.status = 'pending'), n.catch(() => {}));
  function r(s) {
    (Object.assign(n, s), delete n.resolve, delete n.reject);
  }
  return (
    (n.resolve = (s) => {
      (r({ status: 'fulfilled', value: s }), e(s));
    }),
    (n.reject = (s) => {
      (r({ status: 'rejected', reason: s }), t(s));
    }),
    n
  );
}
var n0 = qg;
function r0() {
  let e = [],
    t = 0,
    n = (a) => {
      a();
    },
    r = (a) => {
      a();
    },
    s = n0;
  const i = (a) => {
      t
        ? e.push(a)
        : s(() => {
            n(a);
          });
    },
    l = () => {
      const a = e;
      ((e = []),
        a.length &&
          s(() => {
            r(() => {
              a.forEach((o) => {
                n(o);
              });
            });
          }));
    };
  return {
    batch: (a) => {
      let o;
      t++;
      try {
        o = a();
      } finally {
        (t--, t || l());
      }
      return o;
    },
    batchCalls:
      (a) =>
      (...o) => {
        i(() => {
          a(...o);
        });
      },
    schedule: i,
    setNotifyFunction: (a) => {
      n = a;
    },
    setBatchNotifyFunction: (a) => {
      r = a;
    },
    setScheduler: (a) => {
      s = a;
    },
  };
}
var ze = r0(),
  vs,
  Un,
  gs,
  th,
  s0 =
    ((th = class extends Qs {
      constructor() {
        super();
        W(this, vs, !0);
        W(this, Un);
        W(this, gs);
        M(this, gs, (t) => {
          if (!Ur && window.addEventListener) {
            const n = () => t(!0),
              r = () => t(!1);
            return (
              window.addEventListener('online', n, !1),
              window.addEventListener('offline', r, !1),
              () => {
                (window.removeEventListener('online', n), window.removeEventListener('offline', r));
              }
            );
          }
        });
      }
      onSubscribe() {
        v(this, Un) || this.setEventListener(v(this, gs));
      }
      onUnsubscribe() {
        var t;
        this.hasListeners() || ((t = v(this, Un)) == null || t.call(this), M(this, Un, void 0));
      }
      setEventListener(t) {
        var n;
        (M(this, gs, t),
          (n = v(this, Un)) == null || n.call(this),
          M(this, Un, t(this.setOnline.bind(this))));
      }
      setOnline(t) {
        v(this, vs) !== t &&
          (M(this, vs, t),
          this.listeners.forEach((r) => {
            r(t);
          }));
      }
      isOnline() {
        return v(this, vs);
      }
    }),
    (vs = new WeakMap()),
    (Un = new WeakMap()),
    (gs = new WeakMap()),
    th),
  ca = new s0();
function i0(e) {
  return Math.min(1e3 * 2 ** e, 3e4);
}
function Nm(e) {
  return (e ?? 'online') === 'online' ? ca.isOnline() : !0;
}
var vu = class extends Error {
  constructor(e) {
    (super('CancelledError'),
      (this.revert = e == null ? void 0 : e.revert),
      (this.silent = e == null ? void 0 : e.silent));
  }
};
function jm(e) {
  let t = !1,
    n = 0,
    r;
  const s = yu(),
    i = () => s.status !== 'pending',
    l = (_) => {
      var N;
      if (!i()) {
        const y = new vu(_);
        (p(y), (N = e.onCancel) == null || N.call(e, y));
      }
    },
    a = () => {
      t = !0;
    },
    o = () => {
      t = !1;
    },
    u = () => Fc.isFocused() && (e.networkMode === 'always' || ca.isOnline()) && e.canRun(),
    f = () => Nm(e.networkMode) && e.canRun(),
    h = (_) => {
      i() || (r == null || r(), s.resolve(_));
    },
    p = (_) => {
      i() || (r == null || r(), s.reject(_));
    },
    k = () =>
      new Promise((_) => {
        var N;
        ((r = (y) => {
          (i() || u()) && _(y);
        }),
          (N = e.onPause) == null || N.call(e));
      }).then(() => {
        var _;
        ((r = void 0), i() || (_ = e.onContinue) == null || _.call(e));
      }),
    S = () => {
      if (i()) return;
      let _;
      const N = n === 0 ? e.initialPromise : void 0;
      try {
        _ = N ?? e.fn();
      } catch (y) {
        _ = Promise.reject(y);
      }
      Promise.resolve(_)
        .then(h)
        .catch((y) => {
          var O;
          if (i()) return;
          const d = e.retry ?? (Ur ? 0 : 3),
            m = e.retryDelay ?? i0,
            x = typeof m == 'function' ? m(n, y) : m,
            j = d === !0 || (typeof d == 'number' && n < d) || (typeof d == 'function' && d(n, y));
          if (t || !j) {
            p(y);
            return;
          }
          (n++,
            (O = e.onFail) == null || O.call(e, n, y),
            Xg(x)
              .then(() => (u() ? void 0 : k()))
              .then(() => {
                t ? p(y) : S();
              }));
        });
    };
  return {
    promise: s,
    status: () => s.status,
    cancel: l,
    continue: () => (r == null || r(), s),
    cancelRetry: a,
    continueRetry: o,
    canStart: f,
    start: () => (f() ? S() : k().then(S), s),
  };
}
var Er,
  nh,
  Rm =
    ((nh = class {
      constructor() {
        W(this, Er);
      }
      destroy() {
        this.clearGcTimeout();
      }
      scheduleGc() {
        (this.clearGcTimeout(),
          hu(this.gcTime) &&
            M(
              this,
              Er,
              kr.setTimeout(() => {
                this.optionalRemove();
              }, this.gcTime),
            ));
      }
      updateGcTime(e) {
        this.gcTime = Math.max(this.gcTime || 0, e ?? (Ur ? 1 / 0 : 5 * 60 * 1e3));
      }
      clearGcTimeout() {
        v(this, Er) && (kr.clearTimeout(v(this, Er)), M(this, Er, void 0));
      }
    }),
    (Er = new WeakMap()),
    nh),
  Nr,
  xs,
  jt,
  jr,
  Be,
  Qi,
  Rr,
  zt,
  cn,
  rh,
  l0 =
    ((rh = class extends Rm {
      constructor(t) {
        super();
        W(this, zt);
        W(this, Nr);
        W(this, xs);
        W(this, jt);
        W(this, jr);
        W(this, Be);
        W(this, Qi);
        W(this, Rr);
        (M(this, Rr, !1),
          M(this, Qi, t.defaultOptions),
          this.setOptions(t.options),
          (this.observers = []),
          M(this, jr, t.client),
          M(this, jt, v(this, jr).getQueryCache()),
          (this.queryKey = t.queryKey),
          (this.queryHash = t.queryHash),
          M(this, Nr, of(this.options)),
          (this.state = t.state ?? v(this, Nr)),
          this.scheduleGc());
      }
      get meta() {
        return this.options.meta;
      }
      get promise() {
        var t;
        return (t = v(this, Be)) == null ? void 0 : t.promise;
      }
      setOptions(t) {
        if (
          ((this.options = { ...v(this, Qi), ...t }),
          this.updateGcTime(this.options.gcTime),
          this.state && this.state.data === void 0)
        ) {
          const n = of(this.options);
          n.data !== void 0 &&
            (this.setData(n.data, { updatedAt: n.dataUpdatedAt, manual: !0 }), M(this, Nr, n));
        }
      }
      optionalRemove() {
        !this.observers.length && this.state.fetchStatus === 'idle' && v(this, jt).remove(this);
      }
      setData(t, n) {
        const r = mu(this.state.data, t, this.options);
        return (
          ne(this, zt, cn).call(this, {
            data: r,
            type: 'success',
            dataUpdatedAt: n == null ? void 0 : n.updatedAt,
            manual: n == null ? void 0 : n.manual,
          }),
          r
        );
      }
      setState(t, n) {
        ne(this, zt, cn).call(this, { type: 'setState', state: t, setStateOptions: n });
      }
      cancel(t) {
        var r, s;
        const n = (r = v(this, Be)) == null ? void 0 : r.promise;
        return (
          (s = v(this, Be)) == null || s.cancel(t),
          n ? n.then(st).catch(st) : Promise.resolve()
        );
      }
      destroy() {
        (super.destroy(), this.cancel({ silent: !0 }));
      }
      reset() {
        (this.destroy(), this.setState(v(this, Nr)));
      }
      isActive() {
        return this.observers.some((t) => Rt(t.options.enabled, this) !== !1);
      }
      isDisabled() {
        return this.getObserversCount() > 0
          ? !this.isActive()
          : this.options.queryFn === Lc ||
              this.state.dataUpdateCount + this.state.errorUpdateCount === 0;
      }
      isStatic() {
        return this.getObserversCount() > 0
          ? this.observers.some((t) => ir(t.options.staleTime, this) === 'static')
          : !1;
      }
      isStale() {
        return this.getObserversCount() > 0
          ? this.observers.some((t) => t.getCurrentResult().isStale)
          : this.state.data === void 0 || this.state.isInvalidated;
      }
      isStaleByTime(t = 0) {
        return this.state.data === void 0
          ? !0
          : t === 'static'
            ? !1
            : this.state.isInvalidated
              ? !0
              : !km(this.state.dataUpdatedAt, t);
      }
      onFocus() {
        var n;
        const t = this.observers.find((r) => r.shouldFetchOnWindowFocus());
        (t == null || t.refetch({ cancelRefetch: !1 }), (n = v(this, Be)) == null || n.continue());
      }
      onOnline() {
        var n;
        const t = this.observers.find((r) => r.shouldFetchOnReconnect());
        (t == null || t.refetch({ cancelRefetch: !1 }), (n = v(this, Be)) == null || n.continue());
      }
      addObserver(t) {
        this.observers.includes(t) ||
          (this.observers.push(t),
          this.clearGcTimeout(),
          v(this, jt).notify({ type: 'observerAdded', query: this, observer: t }));
      }
      removeObserver(t) {
        this.observers.includes(t) &&
          ((this.observers = this.observers.filter((n) => n !== t)),
          this.observers.length ||
            (v(this, Be) &&
              (v(this, Rr) ? v(this, Be).cancel({ revert: !0 }) : v(this, Be).cancelRetry()),
            this.scheduleGc()),
          v(this, jt).notify({ type: 'observerRemoved', query: this, observer: t }));
      }
      getObserversCount() {
        return this.observers.length;
      }
      invalidate() {
        this.state.isInvalidated || ne(this, zt, cn).call(this, { type: 'invalidate' });
      }
      async fetch(t, n) {
        var o, u, f, h, p, k, S, _, N, y, d, m;
        if (
          this.state.fetchStatus !== 'idle' &&
          ((o = v(this, Be)) == null ? void 0 : o.status()) !== 'rejected'
        ) {
          if (this.state.data !== void 0 && n != null && n.cancelRefetch)
            this.cancel({ silent: !0 });
          else if (v(this, Be)) return (v(this, Be).continueRetry(), v(this, Be).promise);
        }
        if ((t && this.setOptions(t), !this.options.queryFn)) {
          const x = this.observers.find((j) => j.options.queryFn);
          x && this.setOptions(x.options);
        }
        const r = new AbortController(),
          s = (x) => {
            Object.defineProperty(x, 'signal', {
              enumerable: !0,
              get: () => (M(this, Rr, !0), r.signal),
            });
          },
          i = () => {
            const x = Cm(this.options, n),
              O = (() => {
                const A = { client: v(this, jr), queryKey: this.queryKey, meta: this.meta };
                return (s(A), A);
              })();
            return (
              M(this, Rr, !1),
              this.options.persister ? this.options.persister(x, O, this) : x(O)
            );
          },
          a = (() => {
            const x = {
              fetchOptions: n,
              options: this.options,
              queryKey: this.queryKey,
              client: v(this, jr),
              state: this.state,
              fetchFn: i,
            };
            return (s(x), x);
          })();
        ((u = this.options.behavior) == null || u.onFetch(a, this),
          M(this, xs, this.state),
          (this.state.fetchStatus === 'idle' ||
            this.state.fetchMeta !== ((f = a.fetchOptions) == null ? void 0 : f.meta)) &&
            ne(this, zt, cn).call(this, {
              type: 'fetch',
              meta: (h = a.fetchOptions) == null ? void 0 : h.meta,
            }),
          M(
            this,
            Be,
            jm({
              initialPromise: n == null ? void 0 : n.initialPromise,
              fn: a.fetchFn,
              onCancel: (x) => {
                (x instanceof vu &&
                  x.revert &&
                  this.setState({ ...v(this, xs), fetchStatus: 'idle' }),
                  r.abort());
              },
              onFail: (x, j) => {
                ne(this, zt, cn).call(this, { type: 'failed', failureCount: x, error: j });
              },
              onPause: () => {
                ne(this, zt, cn).call(this, { type: 'pause' });
              },
              onContinue: () => {
                ne(this, zt, cn).call(this, { type: 'continue' });
              },
              retry: a.options.retry,
              retryDelay: a.options.retryDelay,
              networkMode: a.options.networkMode,
              canRun: () => !0,
            }),
          ));
        try {
          const x = await v(this, Be).start();
          if (x === void 0) throw new Error(`${this.queryHash} data is undefined`);
          return (
            this.setData(x),
            (k = (p = v(this, jt).config).onSuccess) == null || k.call(p, x, this),
            (_ = (S = v(this, jt).config).onSettled) == null ||
              _.call(S, x, this.state.error, this),
            x
          );
        } catch (x) {
          if (x instanceof vu) {
            if (x.silent) return v(this, Be).promise;
            if (x.revert) {
              if (this.state.data === void 0) throw x;
              return this.state.data;
            }
          }
          throw (
            ne(this, zt, cn).call(this, { type: 'error', error: x }),
            (y = (N = v(this, jt).config).onError) == null || y.call(N, x, this),
            (m = (d = v(this, jt).config).onSettled) == null || m.call(d, this.state.data, x, this),
            x
          );
        } finally {
          this.scheduleGc();
        }
      }
    }),
    (Nr = new WeakMap()),
    (xs = new WeakMap()),
    (jt = new WeakMap()),
    (jr = new WeakMap()),
    (Be = new WeakMap()),
    (Qi = new WeakMap()),
    (Rr = new WeakMap()),
    (zt = new WeakSet()),
    (cn = function (t) {
      const n = (r) => {
        switch (t.type) {
          case 'failed':
            return { ...r, fetchFailureCount: t.failureCount, fetchFailureReason: t.error };
          case 'pause':
            return { ...r, fetchStatus: 'paused' };
          case 'continue':
            return { ...r, fetchStatus: 'fetching' };
          case 'fetch':
            return { ...r, ...Tm(r.data, this.options), fetchMeta: t.meta ?? null };
          case 'success':
            const s = {
              ...r,
              data: t.data,
              dataUpdateCount: r.dataUpdateCount + 1,
              dataUpdatedAt: t.dataUpdatedAt ?? Date.now(),
              error: null,
              isInvalidated: !1,
              status: 'success',
              ...(!t.manual && {
                fetchStatus: 'idle',
                fetchFailureCount: 0,
                fetchFailureReason: null,
              }),
            };
            return (M(this, xs, t.manual ? s : void 0), s);
          case 'error':
            const i = t.error;
            return {
              ...r,
              error: i,
              errorUpdateCount: r.errorUpdateCount + 1,
              errorUpdatedAt: Date.now(),
              fetchFailureCount: r.fetchFailureCount + 1,
              fetchFailureReason: i,
              fetchStatus: 'idle',
              status: 'error',
            };
          case 'invalidate':
            return { ...r, isInvalidated: !0 };
          case 'setState':
            return { ...r, ...t.state };
        }
      };
      ((this.state = n(this.state)),
        ze.batch(() => {
          (this.observers.forEach((r) => {
            r.onQueryUpdate();
          }),
            v(this, jt).notify({ query: this, type: 'updated', action: t }));
        }));
    }),
    rh);
function Tm(e, t) {
  return {
    fetchFailureCount: 0,
    fetchFailureReason: null,
    fetchStatus: Nm(t.networkMode) ? 'fetching' : 'paused',
    ...(e === void 0 && { error: null, status: 'pending' }),
  };
}
function of(e) {
  const t = typeof e.initialData == 'function' ? e.initialData() : e.initialData,
    n = t !== void 0,
    r = n
      ? typeof e.initialDataUpdatedAt == 'function'
        ? e.initialDataUpdatedAt()
        : e.initialDataUpdatedAt
      : 0;
  return {
    data: t,
    dataUpdateCount: 0,
    dataUpdatedAt: n ? (r ?? Date.now()) : 0,
    error: null,
    errorUpdateCount: 0,
    errorUpdatedAt: 0,
    fetchFailureCount: 0,
    fetchFailureReason: null,
    fetchMeta: null,
    isInvalidated: !1,
    status: n ? 'success' : 'pending',
    fetchStatus: 'idle',
  };
}
var ut,
  le,
  Wi,
  tt,
  Tr,
  ws,
  hn,
  Vn,
  Zi,
  _s,
  ks,
  Or,
  Pr,
  $n,
  Ss,
  de,
  oi,
  gu,
  xu,
  wu,
  _u,
  ku,
  Su,
  Cu,
  Om,
  sh,
  a0 =
    ((sh = class extends Qs {
      constructor(t, n) {
        super();
        W(this, de);
        W(this, ut);
        W(this, le);
        W(this, Wi);
        W(this, tt);
        W(this, Tr);
        W(this, ws);
        W(this, hn);
        W(this, Vn);
        W(this, Zi);
        W(this, _s);
        W(this, ks);
        W(this, Or);
        W(this, Pr);
        W(this, $n);
        W(this, Ss, new Set());
        ((this.options = n),
          M(this, ut, t),
          M(this, Vn, null),
          M(this, hn, yu()),
          this.bindMethods(),
          this.setOptions(n));
      }
      bindMethods() {
        this.refetch = this.refetch.bind(this);
      }
      onSubscribe() {
        this.listeners.size === 1 &&
          (v(this, le).addObserver(this),
          uf(v(this, le), this.options) ? ne(this, de, oi).call(this) : this.updateResult(),
          ne(this, de, _u).call(this));
      }
      onUnsubscribe() {
        this.hasListeners() || this.destroy();
      }
      shouldFetchOnReconnect() {
        return Eu(v(this, le), this.options, this.options.refetchOnReconnect);
      }
      shouldFetchOnWindowFocus() {
        return Eu(v(this, le), this.options, this.options.refetchOnWindowFocus);
      }
      destroy() {
        ((this.listeners = new Set()),
          ne(this, de, ku).call(this),
          ne(this, de, Su).call(this),
          v(this, le).removeObserver(this));
      }
      setOptions(t) {
        const n = this.options,
          r = v(this, le);
        if (
          ((this.options = v(this, ut).defaultQueryOptions(t)),
          this.options.enabled !== void 0 &&
            typeof this.options.enabled != 'boolean' &&
            typeof this.options.enabled != 'function' &&
            typeof Rt(this.options.enabled, v(this, le)) != 'boolean')
        )
          throw new Error('Expected enabled to be a boolean or a callback that returns a boolean');
        (ne(this, de, Cu).call(this),
          v(this, le).setOptions(this.options),
          n._defaulted &&
            !ua(this.options, n) &&
            v(this, ut)
              .getQueryCache()
              .notify({ type: 'observerOptionsUpdated', query: v(this, le), observer: this }));
        const s = this.hasListeners();
        (s && cf(v(this, le), r, this.options, n) && ne(this, de, oi).call(this),
          this.updateResult(),
          s &&
            (v(this, le) !== r ||
              Rt(this.options.enabled, v(this, le)) !== Rt(n.enabled, v(this, le)) ||
              ir(this.options.staleTime, v(this, le)) !== ir(n.staleTime, v(this, le))) &&
            ne(this, de, gu).call(this));
        const i = ne(this, de, xu).call(this);
        s &&
          (v(this, le) !== r ||
            Rt(this.options.enabled, v(this, le)) !== Rt(n.enabled, v(this, le)) ||
            i !== v(this, $n)) &&
          ne(this, de, wu).call(this, i);
      }
      getOptimisticResult(t) {
        const n = v(this, ut).getQueryCache().build(v(this, ut), t),
          r = this.createResult(n, t);
        return (
          u0(this, r) &&
            (M(this, tt, r), M(this, ws, this.options), M(this, Tr, v(this, le).state)),
          r
        );
      }
      getCurrentResult() {
        return v(this, tt);
      }
      trackResult(t, n) {
        return new Proxy(t, {
          get: (r, s) => (
            this.trackProp(s),
            n == null || n(s),
            s === 'promise' &&
              !this.options.experimental_prefetchInRender &&
              v(this, hn).status === 'pending' &&
              v(this, hn).reject(
                new Error('experimental_prefetchInRender feature flag is not enabled'),
              ),
            Reflect.get(r, s)
          ),
        });
      }
      trackProp(t) {
        v(this, Ss).add(t);
      }
      getCurrentQuery() {
        return v(this, le);
      }
      refetch({ ...t } = {}) {
        return this.fetch({ ...t });
      }
      fetchOptimistic(t) {
        const n = v(this, ut).defaultQueryOptions(t),
          r = v(this, ut).getQueryCache().build(v(this, ut), n);
        return r.fetch().then(() => this.createResult(r, n));
      }
      fetch(t) {
        return ne(this, de, oi)
          .call(this, { ...t, cancelRefetch: t.cancelRefetch ?? !0 })
          .then(() => (this.updateResult(), v(this, tt)));
      }
      createResult(t, n) {
        var q;
        const r = v(this, le),
          s = this.options,
          i = v(this, tt),
          l = v(this, Tr),
          a = v(this, ws),
          u = t !== r ? t.state : v(this, Wi),
          { state: f } = t;
        let h = { ...f },
          p = !1,
          k;
        if (n._optimisticResults) {
          const P = this.hasListeners(),
            H = !P && uf(t, n),
            G = P && cf(t, r, n, s);
          ((H || G) && (h = { ...h, ...Tm(f.data, t.options) }),
            n._optimisticResults === 'isRestoring' && (h.fetchStatus = 'idle'));
        }
        let { error: S, errorUpdatedAt: _, status: N } = h;
        k = h.data;
        let y = !1;
        if (n.placeholderData !== void 0 && k === void 0 && N === 'pending') {
          let P;
          (i != null &&
          i.isPlaceholderData &&
          n.placeholderData === (a == null ? void 0 : a.placeholderData)
            ? ((P = i.data), (y = !0))
            : (P =
                typeof n.placeholderData == 'function'
                  ? n.placeholderData(
                      (q = v(this, ks)) == null ? void 0 : q.state.data,
                      v(this, ks),
                    )
                  : n.placeholderData),
            P !== void 0 &&
              ((N = 'success'), (k = mu(i == null ? void 0 : i.data, P, n)), (p = !0)));
        }
        if (n.select && k !== void 0 && !y)
          if (i && k === (l == null ? void 0 : l.data) && n.select === v(this, Zi)) k = v(this, _s);
          else
            try {
              (M(this, Zi, n.select),
                (k = n.select(k)),
                (k = mu(i == null ? void 0 : i.data, k, n)),
                M(this, _s, k),
                M(this, Vn, null));
            } catch (P) {
              M(this, Vn, P);
            }
        v(this, Vn) && ((S = v(this, Vn)), (k = v(this, _s)), (_ = Date.now()), (N = 'error'));
        const d = h.fetchStatus === 'fetching',
          m = N === 'pending',
          x = N === 'error',
          j = m && d,
          O = k !== void 0,
          L = {
            status: N,
            fetchStatus: h.fetchStatus,
            isPending: m,
            isSuccess: N === 'success',
            isError: x,
            isInitialLoading: j,
            isLoading: j,
            data: k,
            dataUpdatedAt: h.dataUpdatedAt,
            error: S,
            errorUpdatedAt: _,
            failureCount: h.fetchFailureCount,
            failureReason: h.fetchFailureReason,
            errorUpdateCount: h.errorUpdateCount,
            isFetched: h.dataUpdateCount > 0 || h.errorUpdateCount > 0,
            isFetchedAfterMount:
              h.dataUpdateCount > u.dataUpdateCount || h.errorUpdateCount > u.errorUpdateCount,
            isFetching: d,
            isRefetching: d && !m,
            isLoadingError: x && !O,
            isPaused: h.fetchStatus === 'paused',
            isPlaceholderData: p,
            isRefetchError: x && O,
            isStale: Ic(t, n),
            refetch: this.refetch,
            promise: v(this, hn),
            isEnabled: Rt(n.enabled, t) !== !1,
          };
        if (this.options.experimental_prefetchInRender) {
          const P = (ee) => {
              L.status === 'error' ? ee.reject(L.error) : L.data !== void 0 && ee.resolve(L.data);
            },
            H = () => {
              const ee = M(this, hn, (L.promise = yu()));
              P(ee);
            },
            G = v(this, hn);
          switch (G.status) {
            case 'pending':
              t.queryHash === r.queryHash && P(G);
              break;
            case 'fulfilled':
              (L.status === 'error' || L.data !== G.value) && H();
              break;
            case 'rejected':
              (L.status !== 'error' || L.error !== G.reason) && H();
              break;
          }
        }
        return L;
      }
      updateResult() {
        const t = v(this, tt),
          n = this.createResult(v(this, le), this.options);
        if (
          (M(this, Tr, v(this, le).state),
          M(this, ws, this.options),
          v(this, Tr).data !== void 0 && M(this, ks, v(this, le)),
          ua(n, t))
        )
          return;
        M(this, tt, n);
        const r = () => {
          if (!t) return !0;
          const { notifyOnChangeProps: s } = this.options,
            i = typeof s == 'function' ? s() : s;
          if (i === 'all' || (!i && !v(this, Ss).size)) return !0;
          const l = new Set(i ?? v(this, Ss));
          return (
            this.options.throwOnError && l.add('error'),
            Object.keys(v(this, tt)).some((a) => {
              const o = a;
              return v(this, tt)[o] !== t[o] && l.has(o);
            })
          );
        };
        ne(this, de, Om).call(this, { listeners: r() });
      }
      onQueryUpdate() {
        (this.updateResult(), this.hasListeners() && ne(this, de, _u).call(this));
      }
    }),
    (ut = new WeakMap()),
    (le = new WeakMap()),
    (Wi = new WeakMap()),
    (tt = new WeakMap()),
    (Tr = new WeakMap()),
    (ws = new WeakMap()),
    (hn = new WeakMap()),
    (Vn = new WeakMap()),
    (Zi = new WeakMap()),
    (_s = new WeakMap()),
    (ks = new WeakMap()),
    (Or = new WeakMap()),
    (Pr = new WeakMap()),
    ($n = new WeakMap()),
    (Ss = new WeakMap()),
    (de = new WeakSet()),
    (oi = function (t) {
      ne(this, de, Cu).call(this);
      let n = v(this, le).fetch(this.options, t);
      return ((t != null && t.throwOnError) || (n = n.catch(st)), n);
    }),
    (gu = function () {
      ne(this, de, ku).call(this);
      const t = ir(this.options.staleTime, v(this, le));
      if (Ur || v(this, tt).isStale || !hu(t)) return;
      const r = km(v(this, tt).dataUpdatedAt, t) + 1;
      M(
        this,
        Or,
        kr.setTimeout(() => {
          v(this, tt).isStale || this.updateResult();
        }, r),
      );
    }),
    (xu = function () {
      return (
        (typeof this.options.refetchInterval == 'function'
          ? this.options.refetchInterval(v(this, le))
          : this.options.refetchInterval) ?? !1
      );
    }),
    (wu = function (t) {
      (ne(this, de, Su).call(this),
        M(this, $n, t),
        !(
          Ur ||
          Rt(this.options.enabled, v(this, le)) === !1 ||
          !hu(v(this, $n)) ||
          v(this, $n) === 0
        ) &&
          M(
            this,
            Pr,
            kr.setInterval(
              () => {
                (this.options.refetchIntervalInBackground || Fc.isFocused()) &&
                  ne(this, de, oi).call(this);
              },
              v(this, $n),
            ),
          ));
    }),
    (_u = function () {
      (ne(this, de, gu).call(this), ne(this, de, wu).call(this, ne(this, de, xu).call(this)));
    }),
    (ku = function () {
      v(this, Or) && (kr.clearTimeout(v(this, Or)), M(this, Or, void 0));
    }),
    (Su = function () {
      v(this, Pr) && (kr.clearInterval(v(this, Pr)), M(this, Pr, void 0));
    }),
    (Cu = function () {
      const t = v(this, ut).getQueryCache().build(v(this, ut), this.options);
      if (t === v(this, le)) return;
      const n = v(this, le);
      (M(this, le, t),
        M(this, Wi, t.state),
        this.hasListeners() && (n == null || n.removeObserver(this), t.addObserver(this)));
    }),
    (Om = function (t) {
      ze.batch(() => {
        (t.listeners &&
          this.listeners.forEach((n) => {
            n(v(this, tt));
          }),
          v(this, ut)
            .getQueryCache()
            .notify({ query: v(this, le), type: 'observerResultsUpdated' }));
      });
    }),
    sh);
function o0(e, t) {
  return (
    Rt(t.enabled, e) !== !1 &&
    e.state.data === void 0 &&
    !(e.state.status === 'error' && t.retryOnMount === !1)
  );
}
function uf(e, t) {
  return o0(e, t) || (e.state.data !== void 0 && Eu(e, t, t.refetchOnMount));
}
function Eu(e, t, n) {
  if (Rt(t.enabled, e) !== !1 && ir(t.staleTime, e) !== 'static') {
    const r = typeof n == 'function' ? n(e) : n;
    return r === 'always' || (r !== !1 && Ic(e, t));
  }
  return !1;
}
function cf(e, t, n, r) {
  return (
    (e !== t || Rt(r.enabled, e) === !1) && (!n.suspense || e.state.status !== 'error') && Ic(e, n)
  );
}
function Ic(e, t) {
  return Rt(t.enabled, e) !== !1 && e.isStaleByTime(ir(t.staleTime, e));
}
function u0(e, t) {
  return !ua(e.getCurrentResult(), t);
}
function df(e) {
  return {
    onFetch: (t, n) => {
      var f, h, p, k, S;
      const r = t.options,
        s =
          (p =
            (h = (f = t.fetchOptions) == null ? void 0 : f.meta) == null ? void 0 : h.fetchMore) ==
          null
            ? void 0
            : p.direction,
        i = ((k = t.state.data) == null ? void 0 : k.pages) || [],
        l = ((S = t.state.data) == null ? void 0 : S.pageParams) || [];
      let a = { pages: [], pageParams: [] },
        o = 0;
      const u = async () => {
        let _ = !1;
        const N = (m) => {
            Object.defineProperty(m, 'signal', {
              enumerable: !0,
              get: () => (
                t.signal.aborted
                  ? (_ = !0)
                  : t.signal.addEventListener('abort', () => {
                      _ = !0;
                    }),
                t.signal
              ),
            });
          },
          y = Cm(t.options, t.fetchOptions),
          d = async (m, x, j) => {
            if (_) return Promise.reject();
            if (x == null && m.pages.length) return Promise.resolve(m);
            const A = (() => {
                const H = {
                  client: t.client,
                  queryKey: t.queryKey,
                  pageParam: x,
                  direction: j ? 'backward' : 'forward',
                  meta: t.options.meta,
                };
                return (N(H), H);
              })(),
              L = await y(A),
              { maxPages: q } = t.options,
              P = j ? e0 : Jg;
            return { pages: P(m.pages, L, q), pageParams: P(m.pageParams, x, q) };
          };
        if (s && i.length) {
          const m = s === 'backward',
            x = m ? c0 : ff,
            j = { pages: i, pageParams: l },
            O = x(r, j);
          a = await d(j, O, m);
        } else {
          const m = e ?? i.length;
          do {
            const x = o === 0 ? (l[0] ?? r.initialPageParam) : ff(r, a);
            if (o > 0 && x == null) break;
            ((a = await d(a, x)), o++);
          } while (o < m);
        }
        return a;
      };
      t.options.persister
        ? (t.fetchFn = () => {
            var _, N;
            return (N = (_ = t.options).persister) == null
              ? void 0
              : N.call(
                  _,
                  u,
                  {
                    client: t.client,
                    queryKey: t.queryKey,
                    meta: t.options.meta,
                    signal: t.signal,
                  },
                  n,
                );
          })
        : (t.fetchFn = u);
    },
  };
}
function ff(e, { pages: t, pageParams: n }) {
  const r = t.length - 1;
  return t.length > 0 ? e.getNextPageParam(t[r], t, n[r], n) : void 0;
}
function c0(e, { pages: t, pageParams: n }) {
  var r;
  return t.length > 0
    ? (r = e.getPreviousPageParam) == null
      ? void 0
      : r.call(e, t[0], t, n[0], n)
    : void 0;
}
var Hi,
  Jt,
  nt,
  br,
  en,
  Pn,
  ih,
  d0 =
    ((ih = class extends Rm {
      constructor(t) {
        super();
        W(this, en);
        W(this, Hi);
        W(this, Jt);
        W(this, nt);
        W(this, br);
        (M(this, Hi, t.client),
          (this.mutationId = t.mutationId),
          M(this, nt, t.mutationCache),
          M(this, Jt, []),
          (this.state = t.state || Pm()),
          this.setOptions(t.options),
          this.scheduleGc());
      }
      setOptions(t) {
        ((this.options = t), this.updateGcTime(this.options.gcTime));
      }
      get meta() {
        return this.options.meta;
      }
      addObserver(t) {
        v(this, Jt).includes(t) ||
          (v(this, Jt).push(t),
          this.clearGcTimeout(),
          v(this, nt).notify({ type: 'observerAdded', mutation: this, observer: t }));
      }
      removeObserver(t) {
        (M(
          this,
          Jt,
          v(this, Jt).filter((n) => n !== t),
        ),
          this.scheduleGc(),
          v(this, nt).notify({ type: 'observerRemoved', mutation: this, observer: t }));
      }
      optionalRemove() {
        v(this, Jt).length ||
          (this.state.status === 'pending' ? this.scheduleGc() : v(this, nt).remove(this));
      }
      continue() {
        var t;
        return (
          ((t = v(this, br)) == null ? void 0 : t.continue()) ?? this.execute(this.state.variables)
        );
      }
      async execute(t) {
        var l, a, o, u, f, h, p, k, S, _, N, y, d, m, x, j, O, A, L, q;
        const n = () => {
            ne(this, en, Pn).call(this, { type: 'continue' });
          },
          r = {
            client: v(this, Hi),
            meta: this.options.meta,
            mutationKey: this.options.mutationKey,
          };
        M(
          this,
          br,
          jm({
            fn: () =>
              this.options.mutationFn
                ? this.options.mutationFn(t, r)
                : Promise.reject(new Error('No mutationFn found')),
            onFail: (P, H) => {
              ne(this, en, Pn).call(this, { type: 'failed', failureCount: P, error: H });
            },
            onPause: () => {
              ne(this, en, Pn).call(this, { type: 'pause' });
            },
            onContinue: n,
            retry: this.options.retry ?? 0,
            retryDelay: this.options.retryDelay,
            networkMode: this.options.networkMode,
            canRun: () => v(this, nt).canRun(this),
          }),
        );
        const s = this.state.status === 'pending',
          i = !v(this, br).canStart();
        try {
          if (s) n();
          else {
            (ne(this, en, Pn).call(this, { type: 'pending', variables: t, isPaused: i }),
              await ((a = (l = v(this, nt).config).onMutate) == null
                ? void 0
                : a.call(l, t, this, r)));
            const H = await ((u = (o = this.options).onMutate) == null ? void 0 : u.call(o, t, r));
            H !== this.state.context &&
              ne(this, en, Pn).call(this, {
                type: 'pending',
                context: H,
                variables: t,
                isPaused: i,
              });
          }
          const P = await v(this, br).start();
          return (
            await ((h = (f = v(this, nt).config).onSuccess) == null
              ? void 0
              : h.call(f, P, t, this.state.context, this, r)),
            await ((k = (p = this.options).onSuccess) == null
              ? void 0
              : k.call(p, P, t, this.state.context, r)),
            await ((_ = (S = v(this, nt).config).onSettled) == null
              ? void 0
              : _.call(S, P, null, this.state.variables, this.state.context, this, r)),
            await ((y = (N = this.options).onSettled) == null
              ? void 0
              : y.call(N, P, null, t, this.state.context, r)),
            ne(this, en, Pn).call(this, { type: 'success', data: P }),
            P
          );
        } catch (P) {
          try {
            throw (
              await ((m = (d = v(this, nt).config).onError) == null
                ? void 0
                : m.call(d, P, t, this.state.context, this, r)),
              await ((j = (x = this.options).onError) == null
                ? void 0
                : j.call(x, P, t, this.state.context, r)),
              await ((A = (O = v(this, nt).config).onSettled) == null
                ? void 0
                : A.call(O, void 0, P, this.state.variables, this.state.context, this, r)),
              await ((q = (L = this.options).onSettled) == null
                ? void 0
                : q.call(L, void 0, P, t, this.state.context, r)),
              P
            );
          } finally {
            ne(this, en, Pn).call(this, { type: 'error', error: P });
          }
        } finally {
          v(this, nt).runNext(this);
        }
      }
    }),
    (Hi = new WeakMap()),
    (Jt = new WeakMap()),
    (nt = new WeakMap()),
    (br = new WeakMap()),
    (en = new WeakSet()),
    (Pn = function (t) {
      const n = (r) => {
        switch (t.type) {
          case 'failed':
            return { ...r, failureCount: t.failureCount, failureReason: t.error };
          case 'pause':
            return { ...r, isPaused: !0 };
          case 'continue':
            return { ...r, isPaused: !1 };
          case 'pending':
            return {
              ...r,
              context: t.context,
              data: void 0,
              failureCount: 0,
              failureReason: null,
              error: null,
              isPaused: t.isPaused,
              status: 'pending',
              variables: t.variables,
              submittedAt: Date.now(),
            };
          case 'success':
            return {
              ...r,
              data: t.data,
              failureCount: 0,
              failureReason: null,
              error: null,
              status: 'success',
              isPaused: !1,
            };
          case 'error':
            return {
              ...r,
              data: void 0,
              error: t.error,
              failureCount: r.failureCount + 1,
              failureReason: t.error,
              isPaused: !1,
              status: 'error',
            };
        }
      };
      ((this.state = n(this.state)),
        ze.batch(() => {
          (v(this, Jt).forEach((r) => {
            r.onMutationUpdate(t);
          }),
            v(this, nt).notify({ mutation: this, type: 'updated', action: t }));
        }));
    }),
    ih);
function Pm() {
  return {
    context: void 0,
    data: void 0,
    error: null,
    failureCount: 0,
    failureReason: null,
    isPaused: !1,
    status: 'idle',
    variables: void 0,
    submittedAt: 0,
  };
}
var pn,
  Ut,
  Ki,
  lh,
  f0 =
    ((lh = class extends Qs {
      constructor(t = {}) {
        super();
        W(this, pn);
        W(this, Ut);
        W(this, Ki);
        ((this.config = t), M(this, pn, new Set()), M(this, Ut, new Map()), M(this, Ki, 0));
      }
      build(t, n, r) {
        const s = new d0({
          client: t,
          mutationCache: this,
          mutationId: ++ll(this, Ki)._,
          options: t.defaultMutationOptions(n),
          state: r,
        });
        return (this.add(s), s);
      }
      add(t) {
        v(this, pn).add(t);
        const n = Cl(t);
        if (typeof n == 'string') {
          const r = v(this, Ut).get(n);
          r ? r.push(t) : v(this, Ut).set(n, [t]);
        }
        this.notify({ type: 'added', mutation: t });
      }
      remove(t) {
        if (v(this, pn).delete(t)) {
          const n = Cl(t);
          if (typeof n == 'string') {
            const r = v(this, Ut).get(n);
            if (r)
              if (r.length > 1) {
                const s = r.indexOf(t);
                s !== -1 && r.splice(s, 1);
              } else r[0] === t && v(this, Ut).delete(n);
          }
        }
        this.notify({ type: 'removed', mutation: t });
      }
      canRun(t) {
        const n = Cl(t);
        if (typeof n == 'string') {
          const r = v(this, Ut).get(n),
            s = r == null ? void 0 : r.find((i) => i.state.status === 'pending');
          return !s || s === t;
        } else return !0;
      }
      runNext(t) {
        var r;
        const n = Cl(t);
        if (typeof n == 'string') {
          const s =
            (r = v(this, Ut).get(n)) == null ? void 0 : r.find((i) => i !== t && i.state.isPaused);
          return (s == null ? void 0 : s.continue()) ?? Promise.resolve();
        } else return Promise.resolve();
      }
      clear() {
        ze.batch(() => {
          (v(this, pn).forEach((t) => {
            this.notify({ type: 'removed', mutation: t });
          }),
            v(this, pn).clear(),
            v(this, Ut).clear());
        });
      }
      getAll() {
        return Array.from(v(this, pn));
      }
      find(t) {
        const n = { exact: !0, ...t };
        return this.getAll().find((r) => sf(n, r));
      }
      findAll(t = {}) {
        return this.getAll().filter((n) => sf(t, n));
      }
      notify(t) {
        ze.batch(() => {
          this.listeners.forEach((n) => {
            n(t);
          });
        });
      }
      resumePausedMutations() {
        const t = this.getAll().filter((n) => n.state.isPaused);
        return ze.batch(() => Promise.all(t.map((n) => n.continue().catch(st))));
      }
    }),
    (pn = new WeakMap()),
    (Ut = new WeakMap()),
    (Ki = new WeakMap()),
    lh);
function Cl(e) {
  var t;
  return (t = e.options.scope) == null ? void 0 : t.id;
}
var mn,
  Bn,
  ct,
  yn,
  wn,
  Dl,
  Nu,
  ah,
  h0 =
    ((ah = class extends Qs {
      constructor(n, r) {
        super();
        W(this, wn);
        W(this, mn);
        W(this, Bn);
        W(this, ct);
        W(this, yn);
        (M(this, mn, n), this.setOptions(r), this.bindMethods(), ne(this, wn, Dl).call(this));
      }
      bindMethods() {
        ((this.mutate = this.mutate.bind(this)), (this.reset = this.reset.bind(this)));
      }
      setOptions(n) {
        var s;
        const r = this.options;
        ((this.options = v(this, mn).defaultMutationOptions(n)),
          ua(this.options, r) ||
            v(this, mn)
              .getMutationCache()
              .notify({ type: 'observerOptionsUpdated', mutation: v(this, ct), observer: this }),
          r != null &&
          r.mutationKey &&
          this.options.mutationKey &&
          Vr(r.mutationKey) !== Vr(this.options.mutationKey)
            ? this.reset()
            : ((s = v(this, ct)) == null ? void 0 : s.state.status) === 'pending' &&
              v(this, ct).setOptions(this.options));
      }
      onUnsubscribe() {
        var n;
        this.hasListeners() || (n = v(this, ct)) == null || n.removeObserver(this);
      }
      onMutationUpdate(n) {
        (ne(this, wn, Dl).call(this), ne(this, wn, Nu).call(this, n));
      }
      getCurrentResult() {
        return v(this, Bn);
      }
      reset() {
        var n;
        ((n = v(this, ct)) == null || n.removeObserver(this),
          M(this, ct, void 0),
          ne(this, wn, Dl).call(this),
          ne(this, wn, Nu).call(this));
      }
      mutate(n, r) {
        var s;
        return (
          M(this, yn, r),
          (s = v(this, ct)) == null || s.removeObserver(this),
          M(this, ct, v(this, mn).getMutationCache().build(v(this, mn), this.options)),
          v(this, ct).addObserver(this),
          v(this, ct).execute(n)
        );
      }
    }),
    (mn = new WeakMap()),
    (Bn = new WeakMap()),
    (ct = new WeakMap()),
    (yn = new WeakMap()),
    (wn = new WeakSet()),
    (Dl = function () {
      var r;
      const n = ((r = v(this, ct)) == null ? void 0 : r.state) ?? Pm();
      M(this, Bn, {
        ...n,
        isPending: n.status === 'pending',
        isSuccess: n.status === 'success',
        isError: n.status === 'error',
        isIdle: n.status === 'idle',
        mutate: this.mutate,
        reset: this.reset,
      });
    }),
    (Nu = function (n) {
      ze.batch(() => {
        var r, s, i, l, a, o, u, f;
        if (v(this, yn) && this.hasListeners()) {
          const h = v(this, Bn).variables,
            p = v(this, Bn).context,
            k = {
              client: v(this, mn),
              meta: this.options.meta,
              mutationKey: this.options.mutationKey,
            };
          (n == null ? void 0 : n.type) === 'success'
            ? ((s = (r = v(this, yn)).onSuccess) == null || s.call(r, n.data, h, p, k),
              (l = (i = v(this, yn)).onSettled) == null || l.call(i, n.data, null, h, p, k))
            : (n == null ? void 0 : n.type) === 'error' &&
              ((o = (a = v(this, yn)).onError) == null || o.call(a, n.error, h, p, k),
              (f = (u = v(this, yn)).onSettled) == null || f.call(u, void 0, n.error, h, p, k));
        }
        this.listeners.forEach((h) => {
          h(v(this, Bn));
        });
      });
    }),
    ah),
  tn,
  oh,
  p0 =
    ((oh = class extends Qs {
      constructor(t = {}) {
        super();
        W(this, tn);
        ((this.config = t), M(this, tn, new Map()));
      }
      build(t, n, r) {
        const s = n.queryKey,
          i = n.queryHash ?? Ac(s, n);
        let l = this.get(i);
        return (
          l ||
            ((l = new l0({
              client: t,
              queryKey: s,
              queryHash: i,
              options: t.defaultQueryOptions(n),
              state: r,
              defaultOptions: t.getQueryDefaults(s),
            })),
            this.add(l)),
          l
        );
      }
      add(t) {
        v(this, tn).has(t.queryHash) ||
          (v(this, tn).set(t.queryHash, t), this.notify({ type: 'added', query: t }));
      }
      remove(t) {
        const n = v(this, tn).get(t.queryHash);
        n &&
          (t.destroy(),
          n === t && v(this, tn).delete(t.queryHash),
          this.notify({ type: 'removed', query: t }));
      }
      clear() {
        ze.batch(() => {
          this.getAll().forEach((t) => {
            this.remove(t);
          });
        });
      }
      get(t) {
        return v(this, tn).get(t);
      }
      getAll() {
        return [...v(this, tn).values()];
      }
      find(t) {
        const n = { exact: !0, ...t };
        return this.getAll().find((r) => rf(n, r));
      }
      findAll(t = {}) {
        const n = this.getAll();
        return Object.keys(t).length > 0 ? n.filter((r) => rf(t, r)) : n;
      }
      notify(t) {
        ze.batch(() => {
          this.listeners.forEach((n) => {
            n(t);
          });
        });
      }
      onFocus() {
        ze.batch(() => {
          this.getAll().forEach((t) => {
            t.onFocus();
          });
        });
      }
      onOnline() {
        ze.batch(() => {
          this.getAll().forEach((t) => {
            t.onOnline();
          });
        });
      }
    }),
    (tn = new WeakMap()),
    oh),
  Te,
  Qn,
  Wn,
  Cs,
  Es,
  Zn,
  Ns,
  js,
  uh,
  m0 =
    ((uh = class {
      constructor(e = {}) {
        W(this, Te);
        W(this, Qn);
        W(this, Wn);
        W(this, Cs);
        W(this, Es);
        W(this, Zn);
        W(this, Ns);
        W(this, js);
        (M(this, Te, e.queryCache || new p0()),
          M(this, Qn, e.mutationCache || new f0()),
          M(this, Wn, e.defaultOptions || {}),
          M(this, Cs, new Map()),
          M(this, Es, new Map()),
          M(this, Zn, 0));
      }
      mount() {
        (ll(this, Zn)._++,
          v(this, Zn) === 1 &&
            (M(
              this,
              Ns,
              Fc.subscribe(async (e) => {
                e && (await this.resumePausedMutations(), v(this, Te).onFocus());
              }),
            ),
            M(
              this,
              js,
              ca.subscribe(async (e) => {
                e && (await this.resumePausedMutations(), v(this, Te).onOnline());
              }),
            )));
      }
      unmount() {
        var e, t;
        (ll(this, Zn)._--,
          v(this, Zn) === 0 &&
            ((e = v(this, Ns)) == null || e.call(this),
            M(this, Ns, void 0),
            (t = v(this, js)) == null || t.call(this),
            M(this, js, void 0)));
      }
      isFetching(e) {
        return v(this, Te).findAll({ ...e, fetchStatus: 'fetching' }).length;
      }
      isMutating(e) {
        return v(this, Qn).findAll({ ...e, status: 'pending' }).length;
      }
      getQueryData(e) {
        var n;
        const t = this.defaultQueryOptions({ queryKey: e });
        return (n = v(this, Te).get(t.queryHash)) == null ? void 0 : n.state.data;
      }
      ensureQueryData(e) {
        const t = this.defaultQueryOptions(e),
          n = v(this, Te).build(this, t),
          r = n.state.data;
        return r === void 0
          ? this.fetchQuery(e)
          : (e.revalidateIfStale && n.isStaleByTime(ir(t.staleTime, n)) && this.prefetchQuery(t),
            Promise.resolve(r));
      }
      getQueriesData(e) {
        return v(this, Te)
          .findAll(e)
          .map(({ queryKey: t, state: n }) => {
            const r = n.data;
            return [t, r];
          });
      }
      setQueryData(e, t, n) {
        const r = this.defaultQueryOptions({ queryKey: e }),
          s = v(this, Te).get(r.queryHash),
          i = s == null ? void 0 : s.state.data,
          l = Gg(t, i);
        if (l !== void 0)
          return v(this, Te)
            .build(this, r)
            .setData(l, { ...n, manual: !0 });
      }
      setQueriesData(e, t, n) {
        return ze.batch(() =>
          v(this, Te)
            .findAll(e)
            .map(({ queryKey: r }) => [r, this.setQueryData(r, t, n)]),
        );
      }
      getQueryState(e) {
        var n;
        const t = this.defaultQueryOptions({ queryKey: e });
        return (n = v(this, Te).get(t.queryHash)) == null ? void 0 : n.state;
      }
      removeQueries(e) {
        const t = v(this, Te);
        ze.batch(() => {
          t.findAll(e).forEach((n) => {
            t.remove(n);
          });
        });
      }
      resetQueries(e, t) {
        const n = v(this, Te);
        return ze.batch(
          () => (
            n.findAll(e).forEach((r) => {
              r.reset();
            }),
            this.refetchQueries({ type: 'active', ...e }, t)
          ),
        );
      }
      cancelQueries(e, t = {}) {
        const n = { revert: !0, ...t },
          r = ze.batch(() =>
            v(this, Te)
              .findAll(e)
              .map((s) => s.cancel(n)),
          );
        return Promise.all(r).then(st).catch(st);
      }
      invalidateQueries(e, t = {}) {
        return ze.batch(
          () => (
            v(this, Te)
              .findAll(e)
              .forEach((n) => {
                n.invalidate();
              }),
            (e == null ? void 0 : e.refetchType) === 'none'
              ? Promise.resolve()
              : this.refetchQueries(
                  {
                    ...e,
                    type:
                      (e == null ? void 0 : e.refetchType) ??
                      (e == null ? void 0 : e.type) ??
                      'active',
                  },
                  t,
                )
          ),
        );
      }
      refetchQueries(e, t = {}) {
        const n = { ...t, cancelRefetch: t.cancelRefetch ?? !0 },
          r = ze.batch(() =>
            v(this, Te)
              .findAll(e)
              .filter((s) => !s.isDisabled() && !s.isStatic())
              .map((s) => {
                let i = s.fetch(void 0, n);
                return (
                  n.throwOnError || (i = i.catch(st)),
                  s.state.fetchStatus === 'paused' ? Promise.resolve() : i
                );
              }),
          );
        return Promise.all(r).then(st);
      }
      fetchQuery(e) {
        const t = this.defaultQueryOptions(e);
        t.retry === void 0 && (t.retry = !1);
        const n = v(this, Te).build(this, t);
        return n.isStaleByTime(ir(t.staleTime, n)) ? n.fetch(t) : Promise.resolve(n.state.data);
      }
      prefetchQuery(e) {
        return this.fetchQuery(e).then(st).catch(st);
      }
      fetchInfiniteQuery(e) {
        return ((e.behavior = df(e.pages)), this.fetchQuery(e));
      }
      prefetchInfiniteQuery(e) {
        return this.fetchInfiniteQuery(e).then(st).catch(st);
      }
      ensureInfiniteQueryData(e) {
        return ((e.behavior = df(e.pages)), this.ensureQueryData(e));
      }
      resumePausedMutations() {
        return ca.isOnline() ? v(this, Qn).resumePausedMutations() : Promise.resolve();
      }
      getQueryCache() {
        return v(this, Te);
      }
      getMutationCache() {
        return v(this, Qn);
      }
      getDefaultOptions() {
        return v(this, Wn);
      }
      setDefaultOptions(e) {
        M(this, Wn, e);
      }
      setQueryDefaults(e, t) {
        v(this, Cs).set(Vr(e), { queryKey: e, defaultOptions: t });
      }
      getQueryDefaults(e) {
        const t = [...v(this, Cs).values()],
          n = {};
        return (
          t.forEach((r) => {
            zi(e, r.queryKey) && Object.assign(n, r.defaultOptions);
          }),
          n
        );
      }
      setMutationDefaults(e, t) {
        v(this, Es).set(Vr(e), { mutationKey: e, defaultOptions: t });
      }
      getMutationDefaults(e) {
        const t = [...v(this, Es).values()],
          n = {};
        return (
          t.forEach((r) => {
            zi(e, r.mutationKey) && Object.assign(n, r.defaultOptions);
          }),
          n
        );
      }
      defaultQueryOptions(e) {
        if (e._defaulted) return e;
        const t = {
          ...v(this, Wn).queries,
          ...this.getQueryDefaults(e.queryKey),
          ...e,
          _defaulted: !0,
        };
        return (
          t.queryHash || (t.queryHash = Ac(t.queryKey, t)),
          t.refetchOnReconnect === void 0 && (t.refetchOnReconnect = t.networkMode !== 'always'),
          t.throwOnError === void 0 && (t.throwOnError = !!t.suspense),
          !t.networkMode && t.persister && (t.networkMode = 'offlineFirst'),
          t.queryFn === Lc && (t.enabled = !1),
          t
        );
      }
      defaultMutationOptions(e) {
        return e != null && e._defaulted
          ? e
          : {
              ...v(this, Wn).mutations,
              ...((e == null ? void 0 : e.mutationKey) && this.getMutationDefaults(e.mutationKey)),
              ...e,
              _defaulted: !0,
            };
      }
      clear() {
        (v(this, Te).clear(), v(this, Qn).clear());
      }
    }),
    (Te = new WeakMap()),
    (Qn = new WeakMap()),
    (Wn = new WeakMap()),
    (Cs = new WeakMap()),
    (Es = new WeakMap()),
    (Zn = new WeakMap()),
    (Ns = new WeakMap()),
    (js = new WeakMap()),
    uh),
  bm = E.createContext(void 0),
  Mc = (e) => {
    const t = E.useContext(bm);
    if (!t) throw new Error('No QueryClient set, use QueryClientProvider to set one');
    return t;
  },
  y0 = ({ client: e, children: t }) => (
    E.useEffect(
      () => (
        e.mount(),
        () => {
          e.unmount();
        }
      ),
      [e],
    ),
    c.jsx(bm.Provider, { value: e, children: t })
  ),
  Am = E.createContext(!1),
  v0 = () => E.useContext(Am);
Am.Provider;
function g0() {
  let e = !1;
  return {
    clearReset: () => {
      e = !1;
    },
    reset: () => {
      e = !0;
    },
    isReset: () => e,
  };
}
var x0 = E.createContext(g0()),
  w0 = () => E.useContext(x0),
  _0 = (e, t) => {
    (e.suspense || e.throwOnError || e.experimental_prefetchInRender) &&
      (t.isReset() || (e.retryOnMount = !1));
  },
  k0 = (e) => {
    E.useEffect(() => {
      e.clearReset();
    }, [e]);
  },
  S0 = ({ result: e, errorResetBoundary: t, throwOnError: n, query: r, suspense: s }) =>
    e.isError &&
    !t.isReset() &&
    !e.isFetching &&
    r &&
    ((s && e.data === void 0) || Em(n, [e.error, r])),
  C0 = (e) => {
    if (e.suspense) {
      const n = (s) => (s === 'static' ? s : Math.max(s ?? 1e3, 1e3)),
        r = e.staleTime;
      ((e.staleTime = typeof r == 'function' ? (...s) => n(r(...s)) : n(r)),
        typeof e.gcTime == 'number' && (e.gcTime = Math.max(e.gcTime, 1e3)));
    }
  },
  E0 = (e, t) => e.isLoading && e.isFetching && !t,
  N0 = (e, t) => (e == null ? void 0 : e.suspense) && t.isPending,
  hf = (e, t, n) =>
    t.fetchOptimistic(e).catch(() => {
      n.clearReset();
    });
function j0(e, t, n) {
  var h, p, k, S, _;
  const r = v0(),
    s = w0(),
    i = Mc(),
    l = i.defaultQueryOptions(e);
  ((p = (h = i.getDefaultOptions().queries) == null ? void 0 : h._experimental_beforeQuery) ==
    null || p.call(h, l),
    (l._optimisticResults = r ? 'isRestoring' : 'optimistic'),
    C0(l),
    _0(l, s),
    k0(s));
  const a = !i.getQueryCache().get(l.queryHash),
    [o] = E.useState(() => new t(i, l)),
    u = o.getOptimisticResult(l),
    f = !r && e.subscribed !== !1;
  if (
    (E.useSyncExternalStore(
      E.useCallback(
        (N) => {
          const y = f ? o.subscribe(ze.batchCalls(N)) : st;
          return (o.updateResult(), y);
        },
        [o, f],
      ),
      () => o.getCurrentResult(),
      () => o.getCurrentResult(),
    ),
    E.useEffect(() => {
      o.setOptions(l);
    }, [l, o]),
    N0(l, u))
  )
    throw hf(l, o, s);
  if (
    S0({
      result: u,
      errorResetBoundary: s,
      throwOnError: l.throwOnError,
      query: i.getQueryCache().get(l.queryHash),
      suspense: l.suspense,
    })
  )
    throw u.error;
  if (
    ((S = (k = i.getDefaultOptions().queries) == null ? void 0 : k._experimental_afterQuery) ==
      null || S.call(k, l, u),
    l.experimental_prefetchInRender && !Ur && E0(u, r))
  ) {
    const N = a
      ? hf(l, o, s)
      : (_ = i.getQueryCache().get(l.queryHash)) == null
        ? void 0
        : _.promise;
    N == null ||
      N.catch(st).finally(() => {
        o.updateResult();
      });
  }
  return l.notifyOnChangeProps ? u : o.trackResult(u);
}
function R0(e, t) {
  return j0(e, a0);
}
function T0(e, t) {
  const n = Mc(),
    [r] = E.useState(() => new h0(n, e));
  E.useEffect(() => {
    r.setOptions(e);
  }, [r, e]);
  const s = E.useSyncExternalStore(
      E.useCallback((l) => r.subscribe(ze.batchCalls(l)), [r]),
      () => r.getCurrentResult(),
      () => r.getCurrentResult(),
    ),
    i = E.useCallback(
      (l, a) => {
        r.mutate(l, a).catch(st);
      },
      [r],
    );
  if (s.error && Em(r.options.throwOnError, [s.error])) throw s.error;
  return { ...s, mutate: i, mutateAsync: s.mutate };
}
/**
 * @remix-run/router v1.23.0
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ function Ui() {
  return (
    (Ui = Object.assign
      ? Object.assign.bind()
      : function (e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = arguments[t];
            for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
          }
          return e;
        }),
    Ui.apply(this, arguments)
  );
}
var qn;
(function (e) {
  ((e.Pop = 'POP'), (e.Push = 'PUSH'), (e.Replace = 'REPLACE'));
})(qn || (qn = {}));
const pf = 'popstate';
function O0(e) {
  e === void 0 && (e = {});
  function t(r, s) {
    let { pathname: i, search: l, hash: a } = r.location;
    return ju(
      '',
      { pathname: i, search: l, hash: a },
      (s.state && s.state.usr) || null,
      (s.state && s.state.key) || 'default',
    );
  }
  function n(r, s) {
    return typeof s == 'string' ? s : da(s);
  }
  return b0(t, n, null, e);
}
function Pe(e, t) {
  if (e === !1 || e === null || typeof e > 'u') throw new Error(t);
}
function Lm(e, t) {
  if (!e) {
    typeof console < 'u' && console.warn(t);
    try {
      throw new Error(t);
    } catch {}
  }
}
function P0() {
  return Math.random().toString(36).substr(2, 8);
}
function mf(e, t) {
  return { usr: e.state, key: e.key, idx: t };
}
function ju(e, t, n, r) {
  return (
    n === void 0 && (n = null),
    Ui(
      { pathname: typeof e == 'string' ? e : e.pathname, search: '', hash: '' },
      typeof t == 'string' ? Ws(t) : t,
      { state: n, key: (t && t.key) || r || P0() },
    )
  );
}
function da(e) {
  let { pathname: t = '/', search: n = '', hash: r = '' } = e;
  return (
    n && n !== '?' && (t += n.charAt(0) === '?' ? n : '?' + n),
    r && r !== '#' && (t += r.charAt(0) === '#' ? r : '#' + r),
    t
  );
}
function Ws(e) {
  let t = {};
  if (e) {
    let n = e.indexOf('#');
    n >= 0 && ((t.hash = e.substr(n)), (e = e.substr(0, n)));
    let r = e.indexOf('?');
    (r >= 0 && ((t.search = e.substr(r)), (e = e.substr(0, r))), e && (t.pathname = e));
  }
  return t;
}
function b0(e, t, n, r) {
  r === void 0 && (r = {});
  let { window: s = document.defaultView, v5Compat: i = !1 } = r,
    l = s.history,
    a = qn.Pop,
    o = null,
    u = f();
  u == null && ((u = 0), l.replaceState(Ui({}, l.state, { idx: u }), ''));
  function f() {
    return (l.state || { idx: null }).idx;
  }
  function h() {
    a = qn.Pop;
    let N = f(),
      y = N == null ? null : N - u;
    ((u = N), o && o({ action: a, location: _.location, delta: y }));
  }
  function p(N, y) {
    a = qn.Push;
    let d = ju(_.location, N, y);
    u = f() + 1;
    let m = mf(d, u),
      x = _.createHref(d);
    try {
      l.pushState(m, '', x);
    } catch (j) {
      if (j instanceof DOMException && j.name === 'DataCloneError') throw j;
      s.location.assign(x);
    }
    i && o && o({ action: a, location: _.location, delta: 1 });
  }
  function k(N, y) {
    a = qn.Replace;
    let d = ju(_.location, N, y);
    u = f();
    let m = mf(d, u),
      x = _.createHref(d);
    (l.replaceState(m, '', x), i && o && o({ action: a, location: _.location, delta: 0 }));
  }
  function S(N) {
    let y = s.location.origin !== 'null' ? s.location.origin : s.location.href,
      d = typeof N == 'string' ? N : da(N);
    return (
      (d = d.replace(/ $/, '%20')),
      Pe(y, 'No window.location.(origin|href) available to create URL for href: ' + d),
      new URL(d, y)
    );
  }
  let _ = {
    get action() {
      return a;
    },
    get location() {
      return e(s, l);
    },
    listen(N) {
      if (o) throw new Error('A history only accepts one active listener');
      return (
        s.addEventListener(pf, h),
        (o = N),
        () => {
          (s.removeEventListener(pf, h), (o = null));
        }
      );
    },
    createHref(N) {
      return t(s, N);
    },
    createURL: S,
    encodeLocation(N) {
      let y = S(N);
      return { pathname: y.pathname, search: y.search, hash: y.hash };
    },
    push: p,
    replace: k,
    go(N) {
      return l.go(N);
    },
  };
  return _;
}
var yf;
(function (e) {
  ((e.data = 'data'), (e.deferred = 'deferred'), (e.redirect = 'redirect'), (e.error = 'error'));
})(yf || (yf = {}));
function A0(e, t, n) {
  return (n === void 0 && (n = '/'), L0(e, t, n));
}
function L0(e, t, n, r) {
  let s = typeof t == 'string' ? Ws(t) : t,
    i = Fs(s.pathname || '/', n);
  if (i == null) return null;
  let l = Fm(e);
  F0(l);
  let a = null;
  for (let o = 0; a == null && o < l.length; ++o) {
    let u = Z0(i);
    a = Q0(l[o], u);
  }
  return a;
}
function Fm(e, t, n, r) {
  (t === void 0 && (t = []), n === void 0 && (n = []), r === void 0 && (r = ''));
  let s = (i, l, a) => {
    let o = {
      relativePath: a === void 0 ? i.path || '' : a,
      caseSensitive: i.caseSensitive === !0,
      childrenIndex: l,
      route: i,
    };
    o.relativePath.startsWith('/') &&
      (Pe(
        o.relativePath.startsWith(r),
        'Absolute route path "' +
          o.relativePath +
          '" nested under path ' +
          ('"' + r + '" is not valid. An absolute child route path ') +
          'must start with the combined path of all its parent routes.',
      ),
      (o.relativePath = o.relativePath.slice(r.length)));
    let u = lr([r, o.relativePath]),
      f = n.concat(o);
    (i.children &&
      i.children.length > 0 &&
      (Pe(
        i.index !== !0,
        'Index routes must not have child routes. Please remove ' +
          ('all child routes from route path "' + u + '".'),
      ),
      Fm(i.children, t, f, u)),
      !(i.path == null && !i.index) && t.push({ path: u, score: $0(u, i.index), routesMeta: f }));
  };
  return (
    e.forEach((i, l) => {
      var a;
      if (i.path === '' || !((a = i.path) != null && a.includes('?'))) s(i, l);
      else for (let o of Im(i.path)) s(i, l, o);
    }),
    t
  );
}
function Im(e) {
  let t = e.split('/');
  if (t.length === 0) return [];
  let [n, ...r] = t,
    s = n.endsWith('?'),
    i = n.replace(/\?$/, '');
  if (r.length === 0) return s ? [i, ''] : [i];
  let l = Im(r.join('/')),
    a = [];
  return (
    a.push(...l.map((o) => (o === '' ? i : [i, o].join('/')))),
    s && a.push(...l),
    a.map((o) => (e.startsWith('/') && o === '' ? '/' : o))
  );
}
function F0(e) {
  e.sort((t, n) =>
    t.score !== n.score
      ? n.score - t.score
      : B0(
          t.routesMeta.map((r) => r.childrenIndex),
          n.routesMeta.map((r) => r.childrenIndex),
        ),
  );
}
const I0 = /^:[\w-]+$/,
  M0 = 3,
  D0 = 2,
  z0 = 1,
  U0 = 10,
  V0 = -2,
  vf = (e) => e === '*';
function $0(e, t) {
  let n = e.split('/'),
    r = n.length;
  return (
    n.some(vf) && (r += V0),
    t && (r += D0),
    n.filter((s) => !vf(s)).reduce((s, i) => s + (I0.test(i) ? M0 : i === '' ? z0 : U0), r)
  );
}
function B0(e, t) {
  return e.length === t.length && e.slice(0, -1).every((r, s) => r === t[s])
    ? e[e.length - 1] - t[t.length - 1]
    : 0;
}
function Q0(e, t, n) {
  let { routesMeta: r } = e,
    s = {},
    i = '/',
    l = [];
  for (let a = 0; a < r.length; ++a) {
    let o = r[a],
      u = a === r.length - 1,
      f = i === '/' ? t : t.slice(i.length) || '/',
      h = Ru({ path: o.relativePath, caseSensitive: o.caseSensitive, end: u }, f),
      p = o.route;
    if (!h) return null;
    (Object.assign(s, h.params),
      l.push({
        params: s,
        pathname: lr([i, h.pathname]),
        pathnameBase: G0(lr([i, h.pathnameBase])),
        route: p,
      }),
      h.pathnameBase !== '/' && (i = lr([i, h.pathnameBase])));
  }
  return l;
}
function Ru(e, t) {
  typeof e == 'string' && (e = { path: e, caseSensitive: !1, end: !0 });
  let [n, r] = W0(e.path, e.caseSensitive, e.end),
    s = t.match(n);
  if (!s) return null;
  let i = s[0],
    l = i.replace(/(.)\/+$/, '$1'),
    a = s.slice(1);
  return {
    params: r.reduce((u, f, h) => {
      let { paramName: p, isOptional: k } = f;
      if (p === '*') {
        let _ = a[h] || '';
        l = i.slice(0, i.length - _.length).replace(/(.)\/+$/, '$1');
      }
      const S = a[h];
      return (k && !S ? (u[p] = void 0) : (u[p] = (S || '').replace(/%2F/g, '/')), u);
    }, {}),
    pathname: i,
    pathnameBase: l,
    pattern: e,
  };
}
function W0(e, t, n) {
  (t === void 0 && (t = !1),
    n === void 0 && (n = !0),
    Lm(
      e === '*' || !e.endsWith('*') || e.endsWith('/*'),
      'Route path "' +
        e +
        '" will be treated as if it were ' +
        ('"' + e.replace(/\*$/, '/*') + '" because the `*` character must ') +
        'always follow a `/` in the pattern. To get rid of this warning, ' +
        ('please change the route path to "' + e.replace(/\*$/, '/*') + '".'),
    ));
  let r = [],
    s =
      '^' +
      e
        .replace(/\/*\*?$/, '')
        .replace(/^\/*/, '/')
        .replace(/[\\.*+^${}|()[\]]/g, '\\$&')
        .replace(
          /\/:([\w-]+)(\?)?/g,
          (l, a, o) => (
            r.push({ paramName: a, isOptional: o != null }),
            o ? '/?([^\\/]+)?' : '/([^\\/]+)'
          ),
        );
  return (
    e.endsWith('*')
      ? (r.push({ paramName: '*' }), (s += e === '*' || e === '/*' ? '(.*)$' : '(?:\\/(.+)|\\/*)$'))
      : n
        ? (s += '\\/*$')
        : e !== '' && e !== '/' && (s += '(?:(?=\\/|$))'),
    [new RegExp(s, t ? void 0 : 'i'), r]
  );
}
function Z0(e) {
  try {
    return e
      .split('/')
      .map((t) => decodeURIComponent(t).replace(/\//g, '%2F'))
      .join('/');
  } catch (t) {
    return (
      Lm(
        !1,
        'The URL path "' +
          e +
          '" could not be decoded because it is is a malformed URL segment. This is probably due to a bad percent ' +
          ('encoding (' + t + ').'),
      ),
      e
    );
  }
}
function Fs(e, t) {
  if (t === '/') return e;
  if (!e.toLowerCase().startsWith(t.toLowerCase())) return null;
  let n = t.endsWith('/') ? t.length - 1 : t.length,
    r = e.charAt(n);
  return r && r !== '/' ? null : e.slice(n) || '/';
}
function H0(e, t) {
  t === void 0 && (t = '/');
  let { pathname: n, search: r = '', hash: s = '' } = typeof e == 'string' ? Ws(e) : e;
  return { pathname: n ? (n.startsWith('/') ? n : K0(n, t)) : t, search: Y0(r), hash: X0(s) };
}
function K0(e, t) {
  let n = t.replace(/\/+$/, '').split('/');
  return (
    e.split('/').forEach((s) => {
      s === '..' ? n.length > 1 && n.pop() : s !== '.' && n.push(s);
    }),
    n.length > 1 ? n.join('/') : '/'
  );
}
function vo(e, t, n, r) {
  return (
    "Cannot include a '" +
    e +
    "' character in a manually specified " +
    ('`to.' + t + '` field [' + JSON.stringify(r) + '].  Please separate it out to the ') +
    ('`to.' + n + '` field. Alternatively you may provide the full path as ') +
    'a string in <Link to="..."> and the router will parse it for you.'
  );
}
function q0(e) {
  return e.filter((t, n) => n === 0 || (t.route.path && t.route.path.length > 0));
}
function Mm(e, t) {
  let n = q0(e);
  return t
    ? n.map((r, s) => (s === n.length - 1 ? r.pathname : r.pathnameBase))
    : n.map((r) => r.pathnameBase);
}
function Dm(e, t, n, r) {
  r === void 0 && (r = !1);
  let s;
  typeof e == 'string'
    ? (s = Ws(e))
    : ((s = Ui({}, e)),
      Pe(!s.pathname || !s.pathname.includes('?'), vo('?', 'pathname', 'search', s)),
      Pe(!s.pathname || !s.pathname.includes('#'), vo('#', 'pathname', 'hash', s)),
      Pe(!s.search || !s.search.includes('#'), vo('#', 'search', 'hash', s)));
  let i = e === '' || s.pathname === '',
    l = i ? '/' : s.pathname,
    a;
  if (l == null) a = n;
  else {
    let h = t.length - 1;
    if (!r && l.startsWith('..')) {
      let p = l.split('/');
      for (; p[0] === '..'; ) (p.shift(), (h -= 1));
      s.pathname = p.join('/');
    }
    a = h >= 0 ? t[h] : '/';
  }
  let o = H0(s, a),
    u = l && l !== '/' && l.endsWith('/'),
    f = (i || l === '.') && n.endsWith('/');
  return (!o.pathname.endsWith('/') && (u || f) && (o.pathname += '/'), o);
}
const lr = (e) => e.join('/').replace(/\/\/+/g, '/'),
  G0 = (e) => e.replace(/\/+$/, '').replace(/^\/*/, '/'),
  Y0 = (e) => (!e || e === '?' ? '' : e.startsWith('?') ? e : '?' + e),
  X0 = (e) => (!e || e === '#' ? '' : e.startsWith('#') ? e : '#' + e);
function J0(e) {
  return (
    e != null &&
    typeof e.status == 'number' &&
    typeof e.statusText == 'string' &&
    typeof e.internal == 'boolean' &&
    'data' in e
  );
}
const zm = ['post', 'put', 'patch', 'delete'];
new Set(zm);
const ex = ['get', ...zm];
new Set(ex);
/**
 * React Router v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ function Vi() {
  return (
    (Vi = Object.assign
      ? Object.assign.bind()
      : function (e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = arguments[t];
            for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
          }
          return e;
        }),
    Vi.apply(this, arguments)
  );
}
const Ia = E.createContext(null),
  Um = E.createContext(null),
  mr = E.createContext(null),
  Ma = E.createContext(null),
  Wr = E.createContext({ outlet: null, matches: [], isDataRoute: !1 }),
  Vm = E.createContext(null);
function tx(e, t) {
  let { relative: n } = t === void 0 ? {} : t;
  el() || Pe(!1);
  let { basename: r, navigator: s } = E.useContext(mr),
    { hash: i, pathname: l, search: a } = Da(e, { relative: n }),
    o = l;
  return (
    r !== '/' && (o = l === '/' ? r : lr([r, l])),
    s.createHref({ pathname: o, search: a, hash: i })
  );
}
function el() {
  return E.useContext(Ma) != null;
}
function tl() {
  return (el() || Pe(!1), E.useContext(Ma).location);
}
function $m(e) {
  E.useContext(mr).static || E.useLayoutEffect(e);
}
function nx() {
  let { isDataRoute: e } = E.useContext(Wr);
  return e ? mx() : rx();
}
function rx() {
  el() || Pe(!1);
  let e = E.useContext(Ia),
    { basename: t, future: n, navigator: r } = E.useContext(mr),
    { matches: s } = E.useContext(Wr),
    { pathname: i } = tl(),
    l = JSON.stringify(Mm(s, n.v7_relativeSplatPath)),
    a = E.useRef(!1);
  return (
    $m(() => {
      a.current = !0;
    }),
    E.useCallback(
      function (u, f) {
        if ((f === void 0 && (f = {}), !a.current)) return;
        if (typeof u == 'number') {
          r.go(u);
          return;
        }
        let h = Dm(u, JSON.parse(l), i, f.relative === 'path');
        (e == null && t !== '/' && (h.pathname = h.pathname === '/' ? t : lr([t, h.pathname])),
          (f.replace ? r.replace : r.push)(h, f.state, f));
      },
      [t, r, l, i, e],
    )
  );
}
function Da(e, t) {
  let { relative: n } = t === void 0 ? {} : t,
    { future: r } = E.useContext(mr),
    { matches: s } = E.useContext(Wr),
    { pathname: i } = tl(),
    l = JSON.stringify(Mm(s, r.v7_relativeSplatPath));
  return E.useMemo(() => Dm(e, JSON.parse(l), i, n === 'path'), [e, l, i, n]);
}
function sx(e, t) {
  return ix(e, t);
}
function ix(e, t, n, r) {
  el() || Pe(!1);
  let { navigator: s } = E.useContext(mr),
    { matches: i } = E.useContext(Wr),
    l = i[i.length - 1],
    a = l ? l.params : {};
  l && l.pathname;
  let o = l ? l.pathnameBase : '/';
  l && l.route;
  let u = tl(),
    f;
  if (t) {
    var h;
    let N = typeof t == 'string' ? Ws(t) : t;
    (o === '/' || ((h = N.pathname) != null && h.startsWith(o)) || Pe(!1), (f = N));
  } else f = u;
  let p = f.pathname || '/',
    k = p;
  if (o !== '/') {
    let N = o.replace(/^\//, '').split('/');
    k = '/' + p.replace(/^\//, '').split('/').slice(N.length).join('/');
  }
  let S = A0(e, { pathname: k }),
    _ = cx(
      S &&
        S.map((N) =>
          Object.assign({}, N, {
            params: Object.assign({}, a, N.params),
            pathname: lr([
              o,
              s.encodeLocation ? s.encodeLocation(N.pathname).pathname : N.pathname,
            ]),
            pathnameBase:
              N.pathnameBase === '/'
                ? o
                : lr([
                    o,
                    s.encodeLocation ? s.encodeLocation(N.pathnameBase).pathname : N.pathnameBase,
                  ]),
          }),
        ),
      i,
      n,
      r,
    );
  return t && _
    ? E.createElement(
        Ma.Provider,
        {
          value: {
            location: Vi({ pathname: '/', search: '', hash: '', state: null, key: 'default' }, f),
            navigationType: qn.Pop,
          },
        },
        _,
      )
    : _;
}
function lx() {
  let e = px(),
    t = J0(e) ? e.status + ' ' + e.statusText : e instanceof Error ? e.message : JSON.stringify(e),
    n = e instanceof Error ? e.stack : null,
    s = { padding: '0.5rem', backgroundColor: 'rgba(200,200,200, 0.5)' };
  return E.createElement(
    E.Fragment,
    null,
    E.createElement('h2', null, 'Unexpected Application Error!'),
    E.createElement('h3', { style: { fontStyle: 'italic' } }, t),
    n ? E.createElement('pre', { style: s }, n) : null,
    null,
  );
}
const ax = E.createElement(lx, null);
class ox extends E.Component {
  constructor(t) {
    (super(t),
      (this.state = { location: t.location, revalidation: t.revalidation, error: t.error }));
  }
  static getDerivedStateFromError(t) {
    return { error: t };
  }
  static getDerivedStateFromProps(t, n) {
    return n.location !== t.location || (n.revalidation !== 'idle' && t.revalidation === 'idle')
      ? { error: t.error, location: t.location, revalidation: t.revalidation }
      : {
          error: t.error !== void 0 ? t.error : n.error,
          location: n.location,
          revalidation: t.revalidation || n.revalidation,
        };
  }
  componentDidCatch(t, n) {
    console.error('React Router caught the following error during render', t, n);
  }
  render() {
    return this.state.error !== void 0
      ? E.createElement(
          Wr.Provider,
          { value: this.props.routeContext },
          E.createElement(Vm.Provider, { value: this.state.error, children: this.props.component }),
        )
      : this.props.children;
  }
}
function ux(e) {
  let { routeContext: t, match: n, children: r } = e,
    s = E.useContext(Ia);
  return (
    s &&
      s.static &&
      s.staticContext &&
      (n.route.errorElement || n.route.ErrorBoundary) &&
      (s.staticContext._deepestRenderedBoundaryId = n.route.id),
    E.createElement(Wr.Provider, { value: t }, r)
  );
}
function cx(e, t, n, r) {
  var s;
  if (
    (t === void 0 && (t = []), n === void 0 && (n = null), r === void 0 && (r = null), e == null)
  ) {
    var i;
    if (!n) return null;
    if (n.errors) e = n.matches;
    else if (
      (i = r) != null &&
      i.v7_partialHydration &&
      t.length === 0 &&
      !n.initialized &&
      n.matches.length > 0
    )
      e = n.matches;
    else return null;
  }
  let l = e,
    a = (s = n) == null ? void 0 : s.errors;
  if (a != null) {
    let f = l.findIndex((h) => h.route.id && (a == null ? void 0 : a[h.route.id]) !== void 0);
    (f >= 0 || Pe(!1), (l = l.slice(0, Math.min(l.length, f + 1))));
  }
  let o = !1,
    u = -1;
  if (n && r && r.v7_partialHydration)
    for (let f = 0; f < l.length; f++) {
      let h = l[f];
      if (((h.route.HydrateFallback || h.route.hydrateFallbackElement) && (u = f), h.route.id)) {
        let { loaderData: p, errors: k } = n,
          S = h.route.loader && p[h.route.id] === void 0 && (!k || k[h.route.id] === void 0);
        if (h.route.lazy || S) {
          ((o = !0), u >= 0 ? (l = l.slice(0, u + 1)) : (l = [l[0]]));
          break;
        }
      }
    }
  return l.reduceRight((f, h, p) => {
    let k,
      S = !1,
      _ = null,
      N = null;
    n &&
      ((k = a && h.route.id ? a[h.route.id] : void 0),
      (_ = h.route.errorElement || ax),
      o &&
        (u < 0 && p === 0
          ? (yx('route-fallback'), (S = !0), (N = null))
          : u === p && ((S = !0), (N = h.route.hydrateFallbackElement || null))));
    let y = t.concat(l.slice(0, p + 1)),
      d = () => {
        let m;
        return (
          k
            ? (m = _)
            : S
              ? (m = N)
              : h.route.Component
                ? (m = E.createElement(h.route.Component, null))
                : h.route.element
                  ? (m = h.route.element)
                  : (m = f),
          E.createElement(ux, {
            match: h,
            routeContext: { outlet: f, matches: y, isDataRoute: n != null },
            children: m,
          })
        );
      };
    return n && (h.route.ErrorBoundary || h.route.errorElement || p === 0)
      ? E.createElement(ox, {
          location: n.location,
          revalidation: n.revalidation,
          component: _,
          error: k,
          children: d(),
          routeContext: { outlet: null, matches: y, isDataRoute: !0 },
        })
      : d();
  }, null);
}
var Bm = (function (e) {
    return (
      (e.UseBlocker = 'useBlocker'),
      (e.UseRevalidator = 'useRevalidator'),
      (e.UseNavigateStable = 'useNavigate'),
      e
    );
  })(Bm || {}),
  Qm = (function (e) {
    return (
      (e.UseBlocker = 'useBlocker'),
      (e.UseLoaderData = 'useLoaderData'),
      (e.UseActionData = 'useActionData'),
      (e.UseRouteError = 'useRouteError'),
      (e.UseNavigation = 'useNavigation'),
      (e.UseRouteLoaderData = 'useRouteLoaderData'),
      (e.UseMatches = 'useMatches'),
      (e.UseRevalidator = 'useRevalidator'),
      (e.UseNavigateStable = 'useNavigate'),
      (e.UseRouteId = 'useRouteId'),
      e
    );
  })(Qm || {});
function dx(e) {
  let t = E.useContext(Ia);
  return (t || Pe(!1), t);
}
function fx(e) {
  let t = E.useContext(Um);
  return (t || Pe(!1), t);
}
function hx(e) {
  let t = E.useContext(Wr);
  return (t || Pe(!1), t);
}
function Wm(e) {
  let t = hx(),
    n = t.matches[t.matches.length - 1];
  return (n.route.id || Pe(!1), n.route.id);
}
function px() {
  var e;
  let t = E.useContext(Vm),
    n = fx(),
    r = Wm();
  return t !== void 0 ? t : (e = n.errors) == null ? void 0 : e[r];
}
function mx() {
  let { router: e } = dx(Bm.UseNavigateStable),
    t = Wm(Qm.UseNavigateStable),
    n = E.useRef(!1);
  return (
    $m(() => {
      n.current = !0;
    }),
    E.useCallback(
      function (s, i) {
        (i === void 0 && (i = {}),
          n.current &&
            (typeof s == 'number' ? e.navigate(s) : e.navigate(s, Vi({ fromRouteId: t }, i))));
      },
      [e, t],
    )
  );
}
const gf = {};
function yx(e, t, n) {
  gf[e] || (gf[e] = !0);
}
function vx(e, t) {
  (e == null || e.v7_startTransition, e == null || e.v7_relativeSplatPath);
}
function ui(e) {
  Pe(!1);
}
function gx(e) {
  let {
    basename: t = '/',
    children: n = null,
    location: r,
    navigationType: s = qn.Pop,
    navigator: i,
    static: l = !1,
    future: a,
  } = e;
  el() && Pe(!1);
  let o = t.replace(/^\/*/, '/'),
    u = E.useMemo(
      () => ({ basename: o, navigator: i, static: l, future: Vi({ v7_relativeSplatPath: !1 }, a) }),
      [o, a, i, l],
    );
  typeof r == 'string' && (r = Ws(r));
  let { pathname: f = '/', search: h = '', hash: p = '', state: k = null, key: S = 'default' } = r,
    _ = E.useMemo(() => {
      let N = Fs(f, o);
      return N == null
        ? null
        : { location: { pathname: N, search: h, hash: p, state: k, key: S }, navigationType: s };
    }, [o, f, h, p, k, S, s]);
  return _ == null
    ? null
    : E.createElement(
        mr.Provider,
        { value: u },
        E.createElement(Ma.Provider, { children: n, value: _ }),
      );
}
function xx(e) {
  let { children: t, location: n } = e;
  return sx(Tu(t), n);
}
new Promise(() => {});
function Tu(e, t) {
  t === void 0 && (t = []);
  let n = [];
  return (
    E.Children.forEach(e, (r, s) => {
      if (!E.isValidElement(r)) return;
      let i = [...t, s];
      if (r.type === E.Fragment) {
        n.push.apply(n, Tu(r.props.children, i));
        return;
      }
      (r.type !== ui && Pe(!1), !r.props.index || !r.props.children || Pe(!1));
      let l = {
        id: r.props.id || i.join('-'),
        caseSensitive: r.props.caseSensitive,
        element: r.props.element,
        Component: r.props.Component,
        index: r.props.index,
        path: r.props.path,
        loader: r.props.loader,
        action: r.props.action,
        errorElement: r.props.errorElement,
        ErrorBoundary: r.props.ErrorBoundary,
        hasErrorBoundary: r.props.ErrorBoundary != null || r.props.errorElement != null,
        shouldRevalidate: r.props.shouldRevalidate,
        handle: r.props.handle,
        lazy: r.props.lazy,
      };
      (r.props.children && (l.children = Tu(r.props.children, i)), n.push(l));
    }),
    n
  );
}
/**
 * React Router DOM v6.30.1
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ function fa() {
  return (
    (fa = Object.assign
      ? Object.assign.bind()
      : function (e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = arguments[t];
            for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
          }
          return e;
        }),
    fa.apply(this, arguments)
  );
}
function Zm(e, t) {
  if (e == null) return {};
  var n = {},
    r = Object.keys(e),
    s,
    i;
  for (i = 0; i < r.length; i++) ((s = r[i]), !(t.indexOf(s) >= 0) && (n[s] = e[s]));
  return n;
}
function wx(e) {
  return !!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey);
}
function _x(e, t) {
  return e.button === 0 && (!t || t === '_self') && !wx(e);
}
const kx = [
    'onClick',
    'relative',
    'reloadDocument',
    'replace',
    'state',
    'target',
    'to',
    'preventScrollReset',
    'viewTransition',
  ],
  Sx = [
    'aria-current',
    'caseSensitive',
    'className',
    'end',
    'style',
    'to',
    'viewTransition',
    'children',
  ],
  Cx = '6';
try {
  window.__reactRouterVersion = Cx;
} catch {}
const Ex = E.createContext({ isTransitioning: !1 }),
  Nx = 'startTransition',
  xf = Fy[Nx];
function jx(e) {
  let { basename: t, children: n, future: r, window: s } = e,
    i = E.useRef();
  i.current == null && (i.current = O0({ window: s, v5Compat: !0 }));
  let l = i.current,
    [a, o] = E.useState({ action: l.action, location: l.location }),
    { v7_startTransition: u } = r || {},
    f = E.useCallback(
      (h) => {
        u && xf ? xf(() => o(h)) : o(h);
      },
      [o, u],
    );
  return (
    E.useLayoutEffect(() => l.listen(f), [l, f]),
    E.useEffect(() => vx(r), [r]),
    E.createElement(gx, {
      basename: t,
      children: n,
      location: a.location,
      navigationType: a.action,
      navigator: l,
      future: r,
    })
  );
}
const Rx =
    typeof window < 'u' &&
    typeof window.document < 'u' &&
    typeof window.document.createElement < 'u',
  Tx = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i,
  Ox = E.forwardRef(function (t, n) {
    let {
        onClick: r,
        relative: s,
        reloadDocument: i,
        replace: l,
        state: a,
        target: o,
        to: u,
        preventScrollReset: f,
        viewTransition: h,
      } = t,
      p = Zm(t, kx),
      { basename: k } = E.useContext(mr),
      S,
      _ = !1;
    if (typeof u == 'string' && Tx.test(u) && ((S = u), Rx))
      try {
        let m = new URL(window.location.href),
          x = u.startsWith('//') ? new URL(m.protocol + u) : new URL(u),
          j = Fs(x.pathname, k);
        x.origin === m.origin && j != null ? (u = j + x.search + x.hash) : (_ = !0);
      } catch {}
    let N = tx(u, { relative: s }),
      y = bx(u, {
        replace: l,
        state: a,
        target: o,
        preventScrollReset: f,
        relative: s,
        viewTransition: h,
      });
    function d(m) {
      (r && r(m), m.defaultPrevented || y(m));
    }
    return E.createElement(
      'a',
      fa({}, p, { href: S || N, onClick: _ || i ? r : d, ref: n, target: o }),
    );
  }),
  El = E.forwardRef(function (t, n) {
    let {
        'aria-current': r = 'page',
        caseSensitive: s = !1,
        className: i = '',
        end: l = !1,
        style: a,
        to: o,
        viewTransition: u,
        children: f,
      } = t,
      h = Zm(t, Sx),
      p = Da(o, { relative: h.relative }),
      k = tl(),
      S = E.useContext(Um),
      { navigator: _, basename: N } = E.useContext(mr),
      y = S != null && Ax(p) && u === !0,
      d = _.encodeLocation ? _.encodeLocation(p).pathname : p.pathname,
      m = k.pathname,
      x = S && S.navigation && S.navigation.location ? S.navigation.location.pathname : null;
    (s || ((m = m.toLowerCase()), (x = x ? x.toLowerCase() : null), (d = d.toLowerCase())),
      x && N && (x = Fs(x, N) || x));
    const j = d !== '/' && d.endsWith('/') ? d.length - 1 : d.length;
    let O = m === d || (!l && m.startsWith(d) && m.charAt(j) === '/'),
      A = x != null && (x === d || (!l && x.startsWith(d) && x.charAt(d.length) === '/')),
      L = { isActive: O, isPending: A, isTransitioning: y },
      q = O ? r : void 0,
      P;
    typeof i == 'function'
      ? (P = i(L))
      : (P = [i, O ? 'active' : null, A ? 'pending' : null, y ? 'transitioning' : null]
          .filter(Boolean)
          .join(' '));
    let H = typeof a == 'function' ? a(L) : a;
    return E.createElement(
      Ox,
      fa({}, h, { 'aria-current': q, className: P, ref: n, style: H, to: o, viewTransition: u }),
      typeof f == 'function' ? f(L) : f,
    );
  });
var Ou;
(function (e) {
  ((e.UseScrollRestoration = 'useScrollRestoration'),
    (e.UseSubmit = 'useSubmit'),
    (e.UseSubmitFetcher = 'useSubmitFetcher'),
    (e.UseFetcher = 'useFetcher'),
    (e.useViewTransitionState = 'useViewTransitionState'));
})(Ou || (Ou = {}));
var wf;
(function (e) {
  ((e.UseFetcher = 'useFetcher'),
    (e.UseFetchers = 'useFetchers'),
    (e.UseScrollRestoration = 'useScrollRestoration'));
})(wf || (wf = {}));
function Px(e) {
  let t = E.useContext(Ia);
  return (t || Pe(!1), t);
}
function bx(e, t) {
  let {
      target: n,
      replace: r,
      state: s,
      preventScrollReset: i,
      relative: l,
      viewTransition: a,
    } = t === void 0 ? {} : t,
    o = nx(),
    u = tl(),
    f = Da(e, { relative: l });
  return E.useCallback(
    (h) => {
      if (_x(h, n)) {
        h.preventDefault();
        let p = r !== void 0 ? r : da(u) === da(f);
        o(e, { replace: p, state: s, preventScrollReset: i, relative: l, viewTransition: a });
      }
    },
    [u, o, f, r, s, n, e, i, l, a],
  );
}
function Ax(e, t) {
  t === void 0 && (t = {});
  let n = E.useContext(Ex);
  n == null && Pe(!1);
  let { basename: r } = Px(Ou.useViewTransitionState),
    s = Da(e, { relative: t.relative });
  if (!n.isTransitioning) return !1;
  let i = Fs(n.currentLocation.pathname, r) || n.currentLocation.pathname,
    l = Fs(n.nextLocation.pathname, r) || n.nextLocation.pathname;
  return Ru(s.pathname, l) != null || Ru(s.pathname, i) != null;
}
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Lx = (e) => e.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase(),
  Hm = (...e) => e.filter((t, n, r) => !!t && r.indexOf(t) === n).join(' ');
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ var Fx = {
  xmlns: 'http://www.w3.org/2000/svg',
  width: 24,
  height: 24,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Ix = E.forwardRef(
  (
    {
      color: e = 'currentColor',
      size: t = 24,
      strokeWidth: n = 2,
      absoluteStrokeWidth: r,
      className: s = '',
      children: i,
      iconNode: l,
      ...a
    },
    o,
  ) =>
    E.createElement(
      'svg',
      {
        ref: o,
        ...Fx,
        width: t,
        height: t,
        stroke: e,
        strokeWidth: r ? (Number(n) * 24) / Number(t) : n,
        className: Hm('lucide', s),
        ...a,
      },
      [...l.map(([u, f]) => E.createElement(u, f)), ...(Array.isArray(i) ? i : [i])],
    ),
);
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const za = (e, t) => {
  const n = E.forwardRef(({ className: r, ...s }, i) =>
    E.createElement(Ix, { ref: i, iconNode: t, className: Hm(`lucide-${Lx(e)}`, r), ...s }),
  );
  return ((n.displayName = `${e}`), n);
};
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Kr = za('CircleAlert', [
  ['circle', { cx: '12', cy: '12', r: '10', key: '1mglay' }],
  ['line', { x1: '12', x2: '12', y1: '8', y2: '12', key: '1pkeuh' }],
  ['line', { x1: '12', x2: '12.01', y1: '16', y2: '16', key: '4dfq90' }],
]);
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Mx = za('LoaderCircle', [['path', { d: 'M21 12a9 9 0 1 1-6.219-8.56', key: '13zald' }]]);
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Dx = za('TrendingUp', [
  ['polyline', { points: '22 7 13.5 15.5 8.5 10.5 2 17', key: '126l90' }],
  ['polyline', { points: '16 7 22 7 22 13', key: 'kwv8wd' }],
]);
/**
 * @license lucide-react v0.453.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const zx = za('TriangleAlert', [
  [
    'path',
    {
      d: 'm21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3',
      key: 'wmoenq',
    },
  ],
  ['path', { d: 'M12 9v4', key: 'juzpu7' }],
  ['path', { d: 'M12 17h.01', key: 'p32p05' }],
]);
function On({ rows: e = 3 }) {
  return c.jsx('div', {
    className: 'space-y-2',
    children: Array.from({ length: e }).map((t, n) =>
      c.jsx('div', { className: 'h-4 bg-gray-200 rounded w-full animate-pulse' }, n),
    ),
  });
}
function Km({ message: e, type: t = 'info', onClose: n }) {
  const [r, s] = E.useState(!0);
  if (
    (E.useEffect(() => {
      const l = setTimeout(() => {
        (s(!1), n());
      }, 3e3);
      return () => clearTimeout(l);
    }, []),
    !r)
  )
    return null;
  const i =
    t === 'error'
      ? 'bg-red-100 text-red-800 border-red-300'
      : t === 'success'
        ? 'bg-green-100 text-green-800 border-green-300'
        : 'bg-blue-100 text-blue-800 border-blue-300';
  return c.jsx('div', {
    className: `fixed right-4 bottom-4 border rounded-lg px-3 py-2 text-sm shadow ${i}`,
    children: e,
  });
}
const Ux = 'true'.toLowerCase(),
  Vx = 'Beta recommendations - verify before betting',
  $x = 'Beta Mode - View Only',
  Bx = new Set(['true', '1', 'yes', 'on']),
  qm = Bx.has(Ux),
  Gm = Vx,
  Ym = $x;
function Qx() {
  var e;
  return typeof window < 'u' && ((e = window.location) == null ? void 0 : e.protocol) === 'https:'
    ? 'https'
    : 'http';
}
function Wx() {
  var e;
  return typeof window < 'u' && (e = window.location) != null && e.hostname
    ? window.location.hostname
    : 'localhost';
}
const ni = 'http://localhost:8000'.trim();
function Zx() {
  const e = Qx(),
    t = Wx();
  return ni.length > 0 && !ni.includes('api:')
    ? ni
    : ni.length > 0 && ni.includes('api:') && typeof window < 'u'
      ? `${e}://${t}:8000`
      : `${e}://${t}:8000`;
}
const Xm = Zx().replace(/\/$/, ''),
  Hx = `${Xm}/api/edges/current`,
  Kx = 5 * 60 * 1e3,
  _f = 3,
  qx = 1500,
  Gx = 1500,
  Yx = (e) => new Promise((t) => setTimeout(t, e));
function Xx() {
  const [e, t] = E.useState(null),
    [n, r] = E.useState(null),
    [s, i] = E.useState(!0),
    [l, a] = E.useState(!1),
    [o, u] = E.useState(null),
    [f, h] = E.useState(null),
    [p, k] = E.useState('confidence'),
    [S, _] = E.useState('all'),
    [N, y] = E.useState('all'),
    [d, m] = E.useState(''),
    [x, j] = E.useState(null),
    [O, A] = E.useState(null),
    L = E.useRef(null),
    q = E.useRef(0),
    P = E.useCallback(async () => {
      var fe;
      const F = L.current === null;
      F ? i(!0) : a(!0);
      let te = null;
      try {
        for (let Ce = 0; Ce < _f; Ce += 1)
          try {
            const me = await fetch(Hx);
            if (!me.ok) throw new Error(`Request failed with status ${me.status}`);
            const Ve = await me.json(),
              qt = (jn) =>
                `${jn.type ?? 'Unknown Edge'}-${jn.player ?? 'Unknown Player'}-${jn.team ?? 'Unknown Team'}`,
              Zr = ((fe = L.current) == null ? void 0 : fe.edges) ?? [];
            if (((L.current = Ve), t(Ve), u(null), h(null), j(new Date()), !F)) {
              const jn = new Set(Zr.map((C) => qt(C))),
                sl = new Set(Ve.edges.map((C) => qt(C))),
                g = Ve.edges.filter((C) => !jn.has(qt(C))).length,
                w = Zr.filter((C) => !sl.has(qt(C))).length;
              g > 0
                ? A({ message: `${g} new edge${g === 1 ? '' : 's'} detected.`, type: 'success' })
                : w > 0 &&
                  A({
                    message: `${w} edge${w === 1 ? '' : 's'} removed from the list.`,
                    type: 'info',
                  });
            }
            return;
          } catch (me) {
            ((te = me instanceof Error ? me : new Error('Unknown error fetching edges')),
              Ce < _f - 1 && (await Yx(qx * (Ce + 1))));
          }
        (u('We could not reach the edges service. Confirm the backend is running and try again.'),
          h((te == null ? void 0 : te.message) ?? null));
      } finally {
        F ? i(!1) : a(!1);
      }
    }, []),
    H = E.useCallback(
      (F) => {
        const te = Date.now();
        (!(F != null && F.bypassDebounce) && te - q.current < Gx) || ((q.current = te), P());
      },
      [P],
    );
  E.useEffect(() => {
    P();
    const F = setInterval(P, Kx);
    return () => clearInterval(F);
  }, [P]);
  const G = E.useCallback(
      (F) =>
        F >= 0.8
          ? 'text-green-600 bg-green-100'
          : F >= 0.65
            ? 'text-yellow-600 bg-yellow-100'
            : 'text-red-600 bg-red-100',
      [],
    ),
    ee = E.useMemo(() => {
      if (!e) return { label: 'Unknown', color: 'bg-gray-400', percent: '—' };
      const F = e.data_quality,
        te = `${Math.round(F * 100)}%`;
      return F >= 0.8
        ? { label: 'Fresh', color: 'bg-green-500', percent: te }
        : F >= 0.5
          ? { label: 'Recent', color: 'bg-yellow-500', percent: te }
          : { label: 'Stale', color: 'bg-red-500', percent: te };
    }, [e]),
    ve = Ym,
    ae = (e == null ? void 0 : e.edges) ?? [],
    ie = e == null ? void 0 : e.summary,
    qe = !!(e != null && e.beta_mode),
    D = e == null ? void 0 : e.disclaimer,
    K = !!(e != null && e.view_only),
    Y = D || Gm,
    ge = ie != null && ie.generated_at ? new Date(ie.generated_at).toLocaleString() : 'Unknown',
    Re = E.useMemo(() => {
      const F = new Set();
      return (
        ae.forEach((te) => {
          F.add(te.type || 'Unknown Edge');
        }),
        Array.from(F).sort((te, fe) => te.localeCompare(fe))
      );
    }, [ae]),
    an = E.useMemo(() => {
      const F = new Set();
      return (
        ae.forEach((te) => {
          te.team && F.add(te.team);
        }),
        Array.from(F).sort((te, fe) => te.localeCompare(fe))
      );
    }, [ae]),
    Et = E.useMemo(() => {
      const F = (me) => (typeof me == 'number' && Number.isFinite(me) ? me : 0),
        te = d.trim().toLowerCase(),
        fe = ae.filter((me) => {
          const Ve = S === 'all' || (me.type || 'Unknown Edge') === S,
            qt = N === 'all' || (me.team || 'Unknown Team') === N,
            Zr =
              te.length === 0 ||
              [me.player, me.team, me.type]
                .filter(Boolean)
                .some((jn) => String(jn).toLowerCase().includes(te));
          return Ve && qt && Zr;
        });
      if (p === 'default') return fe;
      const Ce = fe.slice();
      switch (p) {
        case 'confidence':
          Ce.sort((me, Ve) => F(Ve.confidence) - F(me.confidence));
          break;
        case 'expected_value':
          Ce.sort((me, Ve) => F(Ve.expected_value) - F(me.expected_value));
          break;
        case 'alphabetical':
          Ce.sort((me, Ve) => (me.player || '').localeCompare(Ve.player || ''));
          break;
      }
      return Ce;
    }, [ae, p, S, N, d]),
    on = Et.length,
    It = (ie == null ? void 0 : ie.total_edges) ?? ae.length,
    Kt = on > 0,
    rl = x ? x.toLocaleTimeString() : '—',
    Zs = E.useCallback(() => {
      (k('confidence'), _('all'), y('all'), m(''));
    }, []);
  return s && ae.length === 0
    ? c.jsxs('div', {
        className: 'p-6 max-w-7xl mx-auto space-y-6',
        'aria-busy': 'true',
        children: [
          c.jsxs('div', {
            className: 'space-y-3',
            children: [
              c.jsx('div', { className: 'h-6 w-48 rounded bg-gray-200 animate-pulse' }),
              c.jsx('div', { className: 'h-4 w-72 rounded bg-gray-200 animate-pulse' }),
            ],
          }),
          c.jsx('div', {
            className: 'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4',
            children: Array.from({ length: 4 }).map((F, te) =>
              c.jsx(
                'div',
                { className: 'bg-white p-4 rounded-lg shadow', children: c.jsx(On, { rows: 2 }) },
                `summary-skeleton-${te}`,
              ),
            ),
          }),
          c.jsx('div', {
            className: 'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
            children: Array.from({ length: 6 }).map((F, te) =>
              c.jsx(
                'div',
                {
                  className: 'bg-white p-4 rounded-lg shadow border border-gray-100',
                  children: c.jsx(On, { rows: 4 }),
                },
                `edge-skeleton-${te}`,
              ),
            ),
          }),
        ],
      })
    : o && ae.length === 0
      ? c.jsx('div', {
          className: 'p-6 max-w-xl mx-auto',
          children: c.jsxs('div', {
            className: 'rounded-lg border border-red-200 bg-red-50 p-6 space-y-4',
            role: 'alert',
            'aria-live': 'assertive',
            children: [
              c.jsxs('div', {
                className: 'flex items-start gap-3',
                children: [
                  c.jsx(Kr, { className: 'h-6 w-6 text-red-600 mt-0.5', 'aria-hidden': !0 }),
                  c.jsxs('div', {
                    children: [
                      c.jsx('p', {
                        className: 'text-lg font-semibold text-red-800',
                        children: 'Cannot reach the edges service',
                      }),
                      c.jsx('p', {
                        className: 'text-sm text-red-700',
                        children:
                          'Make sure the Docker stack is running on ports 5173 and 8000, then retry.',
                      }),
                      f &&
                        c.jsxs('p', {
                          className: 'mt-2 text-xs text-red-600',
                          children: ['Details: ', f],
                        }),
                    ],
                  }),
                ],
              }),
              c.jsx('button', {
                type: 'button',
                onClick: () => H({ bypassDebounce: !0 }),
                className:
                  'inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700',
                children: 'Retry',
              }),
            ],
          }),
        })
      : !e && !s && !o
        ? c.jsx('div', { className: 'p-4', children: 'No data available' })
        : (E.useEffect(() => {
            const F = () => {
              document.visibilityState === 'visible' && H({ bypassDebounce: !0 });
            };
            return (
              document.addEventListener('visibilitychange', F),
              () => document.removeEventListener('visibilitychange', F)
            );
          }, [H]),
          s && ae.length === 0
            ? c.jsxs('div', {
                className: 'p-6 max-w-7xl mx-auto space-y-6',
                'aria-busy': 'true',
                children: [
                  c.jsxs('div', {
                    className: 'space-y-3',
                    children: [
                      c.jsx('div', { className: 'h-6 w-48 rounded bg-gray-200 animate-pulse' }),
                      c.jsx('div', { className: 'h-4 w-72 rounded bg-gray-200 animate-pulse' }),
                    ],
                  }),
                  c.jsx('div', {
                    className: 'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4',
                    children: Array.from({ length: 4 }).map((F, te) =>
                      c.jsx(
                        'div',
                        {
                          className: 'bg-white p-4 rounded-lg shadow',
                          children: c.jsx(On, { rows: 2 }),
                        },
                        `summary-skeleton-${te}`,
                      ),
                    ),
                  }),
                  c.jsx('div', {
                    className: 'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
                    children: Array.from({ length: 6 }).map((F, te) =>
                      c.jsx(
                        'div',
                        {
                          className: 'bg-white p-4 rounded-lg shadow border border-gray-100',
                          children: c.jsx(On, { rows: 4 }),
                        },
                        `edge-skeleton-${te}`,
                      ),
                    ),
                  }),
                ],
              })
            : o && ae.length === 0
              ? c.jsx('div', {
                  className: 'p-6 max-w-xl mx-auto',
                  children: c.jsxs('div', {
                    className: 'rounded-lg border border-red-200 bg-red-50 p-6 space-y-4',
                    role: 'alert',
                    'aria-live': 'assertive',
                    children: [
                      c.jsxs('div', {
                        className: 'flex items-start gap-3',
                        children: [
                          c.jsx(Kr, {
                            className: 'h-6 w-6 text-red-600 mt-0.5',
                            'aria-hidden': !0,
                          }),
                          c.jsxs('div', {
                            children: [
                              c.jsx('p', {
                                className: 'text-lg font-semibold text-red-800',
                                children: 'Cannot reach the edges service',
                              }),
                              c.jsx('p', {
                                className: 'text-sm text-red-700',
                                children:
                                  'Make sure the Docker stack is running on ports 5173 and 8000, then retry.',
                              }),
                              f &&
                                c.jsxs('p', {
                                  className: 'mt-2 text-xs text-red-600',
                                  children: ['Details: ', f],
                                }),
                            ],
                          }),
                        ],
                      }),
                      c.jsx('button', {
                        type: 'button',
                        onClick: () => H({ bypassDebounce: !0 }),
                        className:
                          'inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700',
                        children: 'Retry',
                      }),
                    ],
                  }),
                })
              : !e && !s && !o
                ? c.jsx('div', { className: 'p-4', children: 'No data available' })
                : (E.useEffect(() => {
                    const F = () => {
                      document.visibilityState === 'visible' && H({ bypassDebounce: !0 });
                    };
                    return (
                      document.addEventListener('visibilitychange', F),
                      () => document.removeEventListener('visibilitychange', F)
                    );
                  }, [H]),
                  c.jsxs('div', {
                    className: 'p-6 max-w-7xl mx-auto space-y-6',
                    children: [
                      o &&
                        c.jsxs('div', {
                          role: 'alert',
                          className:
                            'flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4',
                          children: [
                            c.jsx(Kr, {
                              className: 'h-5 w-5 text-red-600 mt-0.5',
                              'aria-hidden': !0,
                            }),
                            c.jsxs('div', {
                              className: 'flex-1',
                              children: [
                                c.jsx('p', {
                                  className: 'font-semibold text-red-800',
                                  children: 'Live data refresh failed.',
                                }),
                                c.jsx('p', {
                                  className: 'text-sm text-red-700',
                                  children:
                                    'Showing the last successful snapshot. Retry when ready.',
                                }),
                                f &&
                                  c.jsxs('p', {
                                    className: 'mt-1 text-xs text-red-600',
                                    children: ['Details: ', f],
                                  }),
                              ],
                            }),
                            c.jsx('button', {
                              type: 'button',
                              onClick: () => H({ bypassDebounce: !0 }),
                              className:
                                'rounded bg-red-600 px-3 py-1 text-sm font-medium text-white transition hover:bg-red-700',
                              children: 'Retry',
                            }),
                          ],
                        }),
                      qe &&
                        c.jsxs('div', {
                          role: 'alert',
                          'aria-live': 'assertive',
                          className:
                            'p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3',
                          children: [
                            c.jsx(zx, {
                              className: 'h-5 w-5 text-yellow-600 mt-0.5',
                              'aria-hidden': !0,
                            }),
                            c.jsxs('div', {
                              children: [
                                c.jsx('p', {
                                  className: 'font-semibold text-yellow-800',
                                  children: ve,
                                }),
                                c.jsx('p', { className: 'text-sm text-yellow-700', children: Y }),
                              ],
                            }),
                          ],
                        }),
                      c.jsxs('div', {
                        className:
                          'flex flex-col gap-4 md:flex-row md:items-center md:justify-between',
                        children: [
                          c.jsxs('div', {
                            children: [
                              c.jsx('h1', {
                                className: 'text-2xl font-bold',
                                children: 'Current Edges',
                              }),
                              c.jsx('p', {
                                className: 'text-sm text-gray-600',
                                children:
                                  'Automated discovery — manual verification required before betting.',
                              }),
                            ],
                          }),
                          c.jsxs('div', {
                            className: 'flex items-center gap-3',
                            children: [
                              c.jsxs('div', {
                                className: 'flex items-center gap-2',
                                children: [
                                  c.jsx('span', {
                                    className: 'text-sm text-gray-600',
                                    children: 'Data Quality:',
                                  }),
                                  c.jsxs('span', {
                                    className: `px-2 py-1 rounded text-white text-xs ${ee.color}`,
                                    children: [ee.label, ' (', ee.percent, ')'],
                                  }),
                                ],
                              }),
                              c.jsx('button', {
                                type: 'button',
                                onClick: () => H(),
                                disabled: s || l,
                                className:
                                  'inline-flex items-center gap-2 rounded bg-blue-500 px-3 py-1 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60',
                                children: l
                                  ? c.jsxs(c.Fragment, {
                                      children: [
                                        c.jsx(Mx, {
                                          className: 'h-4 w-4 animate-spin',
                                          'aria-hidden': !0,
                                        }),
                                        'Refreshing…',
                                      ],
                                    })
                                  : 'Refresh',
                              }),
                            ],
                          }),
                        ],
                      }),
                      c.jsxs('div', {
                        className: 'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4',
                        children: [
                          c.jsxs('div', {
                            className: 'bg-white p-4 rounded-lg shadow',
                            children: [
                              c.jsx('p', {
                                className: 'text-sm text-gray-600',
                                children: 'Total Edges',
                              }),
                              c.jsx('p', {
                                className: 'text-2xl font-bold',
                                children: (ie == null ? void 0 : ie.total_edges) ?? 0,
                              }),
                            ],
                          }),
                          c.jsxs('div', {
                            className: 'bg-white p-4 rounded-lg shadow',
                            children: [
                              c.jsx('p', {
                                className: 'text-sm text-gray-600',
                                children: 'Avg Confidence',
                              }),
                              c.jsxs('p', {
                                className: 'text-2xl font-bold',
                                children: [
                                  (((ie == null ? void 0 : ie.avg_confidence) ?? 0) * 100).toFixed(
                                    1,
                                  ),
                                  '%',
                                ],
                              }),
                            ],
                          }),
                          c.jsxs('div', {
                            className: 'bg-white p-4 rounded-lg shadow',
                            children: [
                              c.jsx('p', {
                                className: 'text-sm text-gray-600',
                                children: 'Data Freshness',
                              }),
                              c.jsxs('p', {
                                className: 'text-2xl font-bold',
                                children: [
                                  (((ie == null ? void 0 : ie.data_freshness) ?? 0) * 100).toFixed(
                                    0,
                                  ),
                                  '%',
                                ],
                              }),
                            ],
                          }),
                          c.jsxs('div', {
                            className: 'bg-white p-4 rounded-lg shadow',
                            children: [
                              c.jsx('p', {
                                className: 'text-sm text-gray-600',
                                children: 'Generated',
                              }),
                              c.jsx('p', { className: 'text-sm font-semibold', children: ge }),
                            ],
                          }),
                        ],
                      }),
                      c.jsxs('div', {
                        className:
                          'flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between',
                        children: [
                          c.jsxs('div', {
                            className: 'flex flex-wrap items-center gap-3',
                            children: [
                              c.jsxs('label', {
                                className: 'flex items-center gap-2 text-sm text-gray-600',
                                children: [
                                  'Sort by',
                                  c.jsxs('select', {
                                    value: p,
                                    onChange: (F) => k(F.target.value),
                                    className:
                                      'rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                                    children: [
                                      c.jsx('option', {
                                        value: 'default',
                                        children: 'Default order',
                                      }),
                                      c.jsx('option', {
                                        value: 'confidence',
                                        children: 'Confidence (high → low)',
                                      }),
                                      c.jsx('option', {
                                        value: 'expected_value',
                                        children: 'Expected Value (high → low)',
                                      }),
                                      c.jsx('option', {
                                        value: 'alphabetical',
                                        children: 'Player (A → Z)',
                                      }),
                                    ],
                                  }),
                                ],
                              }),
                              c.jsxs('label', {
                                className: 'flex items-center gap-2 text-sm text-gray-600',
                                children: [
                                  'Edge type',
                                  c.jsxs('select', {
                                    value: S,
                                    onChange: (F) => _(F.target.value),
                                    className:
                                      'rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                                    children: [
                                      c.jsx('option', { value: 'all', children: 'All edge types' }),
                                      Re.map((F) => c.jsx('option', { value: F, children: F }, F)),
                                    ],
                                  }),
                                ],
                              }),
                              c.jsxs('label', {
                                className: 'flex items-center gap-2 text-sm text-gray-600',
                                children: [
                                  'Team',
                                  c.jsxs('select', {
                                    value: N,
                                    onChange: (F) => y(F.target.value),
                                    className:
                                      'rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                                    children: [
                                      c.jsx('option', { value: 'all', children: 'All teams' }),
                                      an.map((F) => c.jsx('option', { value: F, children: F }, F)),
                                    ],
                                  }),
                                ],
                              }),
                            ],
                          }),
                          c.jsxs('div', {
                            className: 'flex flex-wrap items-center gap-3',
                            children: [
                              c.jsx('input', {
                                type: 'search',
                                value: d,
                                onChange: (F) => m(F.target.value),
                                placeholder: 'Search players or teams',
                                className:
                                  'w-full rounded border border-gray-300 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 md:w-64',
                              }),
                              c.jsx('button', {
                                type: 'button',
                                onClick: Zs,
                                className: 'text-sm font-medium text-blue-600 hover:underline',
                                children: 'Reset filters',
                              }),
                              c.jsxs('div', {
                                className: 'flex flex-col text-xs text-gray-500',
                                children: [
                                  c.jsxs('span', {
                                    children: ['Showing ', on, ' of ', It, ' edges'],
                                  }),
                                  c.jsxs('span', { children: ['Last refreshed at ', rl] }),
                                ],
                              }),
                            ],
                          }),
                        ],
                      }),
                      Kt
                        ? c.jsx('div', {
                            className: 'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
                            children: Et.map((F, te) => {
                              const fe = F.player || 'Unknown Player',
                                Ce = F.team || 'Unknown Team',
                                me = F.opponent ? ` vs ${F.opponent}` : '',
                                Ve = Number.isFinite(F.confidence) ? F.confidence : 0,
                                qt = Number.isFinite(F.expected_value) ? F.expected_value : 0;
                              return c.jsxs(
                                'button',
                                {
                                  type: 'button',
                                  className:
                                    'text-left bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow',
                                  onClick: () => r(F),
                                  children: [
                                    c.jsxs('div', {
                                      className: 'flex justify-between items-start mb-2',
                                      children: [
                                        c.jsx('span', {
                                          className:
                                            'text-xs font-semibold text-gray-500 uppercase',
                                          children: F.type,
                                        }),
                                        c.jsx(Dx, {
                                          className: 'h-4 w-4 text-green-500',
                                          'aria-hidden': !0,
                                        }),
                                      ],
                                    }),
                                    c.jsx('h3', {
                                      className: 'font-bold text-lg mb-1',
                                      children: fe,
                                    }),
                                    c.jsxs('p', {
                                      className: 'text-sm text-gray-600 mb-3',
                                      children: [Ce, me],
                                    }),
                                    c.jsxs('div', {
                                      className: 'flex justify-between items-center',
                                      children: [
                                        c.jsxs('div', {
                                          className: 'flex items-center gap-2',
                                          children: [
                                            c.jsxs('span', {
                                              className: `px-2 py-1 rounded text-xs font-semibold ${G(Ve)}`,
                                              children: [(Ve * 100).toFixed(0), '% conf'],
                                            }),
                                            c.jsxs('span', {
                                              className: 'text-xs text-gray-600',
                                              children: ['EV: ', (qt * 100).toFixed(1), '%'],
                                            }),
                                          ],
                                        }),
                                        K &&
                                          c.jsx('span', {
                                            className: 'text-xs text-gray-400',
                                            children: 'View Only',
                                          }),
                                      ],
                                    }),
                                    F.reasoning &&
                                      c.jsx('p', {
                                        className: 'mt-2 text-xs text-gray-500',
                                        children: F.reasoning,
                                      }),
                                  ],
                                },
                                `${fe}-${te}`,
                              );
                            }),
                          })
                        : c.jsx('div', {
                            className:
                              'rounded-lg border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-600',
                            children:
                              'No active edges are available right now. The feed will refresh automatically when new edges appear.',
                          }),
                      n &&
                        c.jsx('div', {
                          className:
                            'fixed inset-0 bg-black/50 flex items-center justify-center z-50',
                          onClick: () => r(null),
                          children: c.jsxs('div', {
                            className: 'bg-white rounded-lg p-6 max-w-md w-full',
                            onClick: (F) => F.stopPropagation(),
                            children: [
                              c.jsx('h2', {
                                className: 'text-xl font-bold mb-4',
                                children: n.player,
                              }),
                              c.jsxs('div', {
                                className: 'space-y-2',
                                children: [
                                  c.jsxs('p', {
                                    children: [
                                      c.jsx('span', {
                                        className: 'font-semibold',
                                        children: 'Type:',
                                      }),
                                      ' ',
                                      n.type,
                                    ],
                                  }),
                                  c.jsxs('p', {
                                    children: [
                                      c.jsx('span', {
                                        className: 'font-semibold',
                                        children: 'Matchup:',
                                      }),
                                      ' ',
                                      n.team,
                                      n.opponent ? ` vs ${n.opponent}` : '',
                                    ],
                                  }),
                                  c.jsxs('p', {
                                    children: [
                                      c.jsx('span', {
                                        className: 'font-semibold',
                                        children: 'Confidence:',
                                      }),
                                      ' ',
                                      (n.confidence * 100).toFixed(1),
                                      '%',
                                    ],
                                  }),
                                  c.jsxs('p', {
                                    children: [
                                      c.jsx('span', {
                                        className: 'font-semibold',
                                        children: 'Expected Value:',
                                      }),
                                      ' ',
                                      (n.expected_value * 100).toFixed(2),
                                      '%',
                                    ],
                                  }),
                                  n.line &&
                                    c.jsxs('p', {
                                      children: [
                                        c.jsx('span', {
                                          className: 'font-semibold',
                                          children: 'Line:',
                                        }),
                                        ' ',
                                        n.line,
                                      ],
                                    }),
                                  n.odds &&
                                    c.jsxs('p', {
                                      children: [
                                        c.jsx('span', {
                                          className: 'font-semibold',
                                          children: 'Odds:',
                                        }),
                                        ' ',
                                        n.odds,
                                      ],
                                    }),
                                  n.reasoning &&
                                    c.jsxs('p', {
                                      children: [
                                        c.jsx('span', {
                                          className: 'font-semibold',
                                          children: 'Analysis:',
                                        }),
                                        ' ',
                                        n.reasoning,
                                      ],
                                    }),
                                  n.notes &&
                                    c.jsxs('p', {
                                      children: [
                                        c.jsx('span', {
                                          className: 'font-semibold',
                                          children: 'Notes:',
                                        }),
                                        ' ',
                                        n.notes,
                                      ],
                                    }),
                                ],
                              }),
                              n.metrics &&
                                c.jsxs('div', {
                                  className: 'mt-4 border-t border-gray-200 pt-4',
                                  children: [
                                    c.jsx('p', {
                                      className: 'font-semibold text-sm text-gray-700',
                                      children: 'Key Metrics',
                                    }),
                                    c.jsx('ul', {
                                      className: 'mt-2 space-y-1 text-sm text-gray-600',
                                      children: Object.entries(n.metrics).map(([F, te]) =>
                                        te && typeof te == 'object'
                                          ? s && ae.length === 0
                                            ? c.jsxs('div', {
                                                className: 'p-6 max-w-7xl mx-auto space-y-6',
                                                'aria-busy': 'true',
                                                children: [
                                                  c.jsxs('div', {
                                                    className: 'space-y-3',
                                                    children: [
                                                      c.jsx('div', {
                                                        className:
                                                          'h-6 w-48 rounded bg-gray-200 animate-pulse',
                                                      }),
                                                      c.jsx('div', {
                                                        className:
                                                          'h-4 w-72 rounded bg-gray-200 animate-pulse',
                                                      }),
                                                    ],
                                                  }),
                                                  c.jsx('div', {
                                                    className:
                                                      'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4',
                                                    children: Array.from({ length: 4 }).map(
                                                      (fe, Ce) =>
                                                        c.jsx(
                                                          'div',
                                                          {
                                                            className:
                                                              'bg-white p-4 rounded-lg shadow',
                                                            children: c.jsx(On, { rows: 2 }),
                                                          },
                                                          `summary-skeleton-${Ce}`,
                                                        ),
                                                    ),
                                                  }),
                                                  c.jsx('div', {
                                                    className:
                                                      'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
                                                    children: Array.from({ length: 6 }).map(
                                                      (fe, Ce) =>
                                                        c.jsx(
                                                          'div',
                                                          {
                                                            className:
                                                              'bg-white p-4 rounded-lg shadow border border-gray-100',
                                                            children: c.jsx(On, { rows: 4 }),
                                                          },
                                                          `edge-skeleton-${Ce}`,
                                                        ),
                                                    ),
                                                  }),
                                                ],
                                              })
                                            : o && ae.length === 0
                                              ? c.jsx('div', {
                                                  className: 'p-6 max-w-xl mx-auto',
                                                  children: c.jsxs('div', {
                                                    className:
                                                      'rounded-lg border border-red-200 bg-red-50 p-6 space-y-4',
                                                    role: 'alert',
                                                    'aria-live': 'assertive',
                                                    children: [
                                                      c.jsxs('div', {
                                                        className: 'flex items-start gap-3',
                                                        children: [
                                                          c.jsx(Kr, {
                                                            className:
                                                              'h-6 w-6 text-red-600 mt-0.5',
                                                            'aria-hidden': !0,
                                                          }),
                                                          c.jsxs('div', {
                                                            children: [
                                                              c.jsx('p', {
                                                                className:
                                                                  'text-lg font-semibold text-red-800',
                                                                children:
                                                                  'Cannot reach the edges service',
                                                              }),
                                                              c.jsx('p', {
                                                                className: 'text-sm text-red-700',
                                                                children:
                                                                  'Make sure the Docker stack is running on ports 5173 and 8000, then retry.',
                                                              }),
                                                              f &&
                                                                c.jsxs('p', {
                                                                  className:
                                                                    'mt-2 text-xs text-red-600',
                                                                  children: ['Details: ', f],
                                                                }),
                                                            ],
                                                          }),
                                                        ],
                                                      }),
                                                      c.jsx('button', {
                                                        type: 'button',
                                                        onClick: () => H({ bypassDebounce: !0 }),
                                                        className:
                                                          'inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700',
                                                        children: 'Retry',
                                                      }),
                                                    ],
                                                  }),
                                                })
                                              : !e && !s && !o
                                                ? c.jsx('div', {
                                                    className: 'p-4',
                                                    children: 'No data available',
                                                  })
                                                : (E.useEffect(() => {
                                                    const fe = () => {
                                                      document.visibilityState === 'visible' &&
                                                        H({ bypassDebounce: !0 });
                                                    };
                                                    return (
                                                      document.addEventListener(
                                                        'visibilitychange',
                                                        fe,
                                                      ),
                                                      () =>
                                                        document.removeEventListener(
                                                          'visibilitychange',
                                                          fe,
                                                        )
                                                    );
                                                  }, [H]),
                                                  c.jsxs(
                                                    'li',
                                                    {
                                                      className: 'text-sm text-gray-600',
                                                      children: [
                                                        c.jsxs('span', {
                                                          className: 'font-semibold capitalize',
                                                          children: [F, ':'],
                                                        }),
                                                        c.jsx('ul', {
                                                          className:
                                                            'ml-4 list-disc text-xs text-gray-500',
                                                          children: Object.entries(te).map(
                                                            ([fe, Ce]) =>
                                                              c.jsxs(
                                                                'li',
                                                                {
                                                                  children: [fe, ': ', String(Ce)],
                                                                },
                                                                `${F}-${fe}`,
                                                              ),
                                                          ),
                                                        }),
                                                      ],
                                                    },
                                                    F,
                                                  ))
                                          : s && ae.length === 0
                                            ? c.jsxs('div', {
                                                className: 'p-6 max-w-7xl mx-auto space-y-6',
                                                'aria-busy': 'true',
                                                children: [
                                                  c.jsxs('div', {
                                                    className: 'space-y-3',
                                                    children: [
                                                      c.jsx('div', {
                                                        className:
                                                          'h-6 w-48 rounded bg-gray-200 animate-pulse',
                                                      }),
                                                      c.jsx('div', {
                                                        className:
                                                          'h-4 w-72 rounded bg-gray-200 animate-pulse',
                                                      }),
                                                    ],
                                                  }),
                                                  c.jsx('div', {
                                                    className:
                                                      'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4',
                                                    children: Array.from({ length: 4 }).map(
                                                      (fe, Ce) =>
                                                        c.jsx(
                                                          'div',
                                                          {
                                                            className:
                                                              'bg-white p-4 rounded-lg shadow',
                                                            children: c.jsx(On, { rows: 2 }),
                                                          },
                                                          `summary-skeleton-${Ce}`,
                                                        ),
                                                    ),
                                                  }),
                                                  c.jsx('div', {
                                                    className:
                                                      'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
                                                    children: Array.from({ length: 6 }).map(
                                                      (fe, Ce) =>
                                                        c.jsx(
                                                          'div',
                                                          {
                                                            className:
                                                              'bg-white p-4 rounded-lg shadow border border-gray-100',
                                                            children: c.jsx(On, { rows: 4 }),
                                                          },
                                                          `edge-skeleton-${Ce}`,
                                                        ),
                                                    ),
                                                  }),
                                                ],
                                              })
                                            : o && ae.length === 0
                                              ? c.jsx('div', {
                                                  className: 'p-6 max-w-xl mx-auto',
                                                  children: c.jsxs('div', {
                                                    className:
                                                      'rounded-lg border border-red-200 bg-red-50 p-6 space-y-4',
                                                    role: 'alert',
                                                    'aria-live': 'assertive',
                                                    children: [
                                                      c.jsxs('div', {
                                                        className: 'flex items-start gap-3',
                                                        children: [
                                                          c.jsx(Kr, {
                                                            className:
                                                              'h-6 w-6 text-red-600 mt-0.5',
                                                            'aria-hidden': !0,
                                                          }),
                                                          c.jsxs('div', {
                                                            children: [
                                                              c.jsx('p', {
                                                                className:
                                                                  'text-lg font-semibold text-red-800',
                                                                children:
                                                                  'Cannot reach the edges service',
                                                              }),
                                                              c.jsx('p', {
                                                                className: 'text-sm text-red-700',
                                                                children:
                                                                  'Make sure the Docker stack is running on ports 5173 and 8000, then retry.',
                                                              }),
                                                              f &&
                                                                c.jsxs('p', {
                                                                  className:
                                                                    'mt-2 text-xs text-red-600',
                                                                  children: ['Details: ', f],
                                                                }),
                                                            ],
                                                          }),
                                                        ],
                                                      }),
                                                      c.jsx('button', {
                                                        type: 'button',
                                                        onClick: () => H({ bypassDebounce: !0 }),
                                                        className:
                                                          'inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700',
                                                        children: 'Retry',
                                                      }),
                                                    ],
                                                  }),
                                                })
                                              : !e && !s && !o
                                                ? c.jsx('div', {
                                                    className: 'p-4',
                                                    children: 'No data available',
                                                  })
                                                : (E.useEffect(() => {
                                                    const fe = () => {
                                                      document.visibilityState === 'visible' &&
                                                        H({ bypassDebounce: !0 });
                                                    };
                                                    return (
                                                      document.addEventListener(
                                                        'visibilitychange',
                                                        fe,
                                                      ),
                                                      () =>
                                                        document.removeEventListener(
                                                          'visibilitychange',
                                                          fe,
                                                        )
                                                    );
                                                  }, [H]),
                                                  c.jsxs(
                                                    'li',
                                                    {
                                                      children: [
                                                        c.jsxs('span', {
                                                          className: 'font-semibold capitalize',
                                                          children: [F, ':'],
                                                        }),
                                                        ' ',
                                                        String(te),
                                                      ],
                                                    },
                                                    F,
                                                  )),
                                      ),
                                    }),
                                  ],
                                }),
                              c.jsx('div', {
                                className: 'mt-6 p-3 bg-yellow-50 rounded',
                                children: c.jsxs('p', {
                                  className: 'text-sm text-yellow-800 flex items-center gap-2',
                                  children: [
                                    c.jsx(Kr, { className: 'h-4 w-4', 'aria-hidden': !0 }),
                                    'Beta mode - Manual verification required before betting',
                                  ],
                                }),
                              }),
                              c.jsx('button', {
                                type: 'button',
                                onClick: () => r(null),
                                className:
                                  'mt-4 w-full py-2 bg-gray-500 text-white rounded hover:bg-gray-600',
                                children: 'Close',
                              }),
                            ],
                          }),
                        }),
                      O && c.jsx(Km, { message: O.message, type: O.type, onClose: () => A(null) }),
                    ],
                  })));
}
class Jx extends Xe.Component {
  constructor(n) {
    super(n);
    Hs(this, 'handleReset', () => {
      this.setState({ hasError: !1, errorMessage: null });
    });
    this.state = { hasError: !1, errorMessage: null };
  }
  static getDerivedStateFromError(n) {
    return { hasError: !0, errorMessage: n.message };
  }
  componentDidCatch(n, r) {
    console.error('Dashboard render error', n, r);
  }
  render() {
    return this.state.hasError
      ? c.jsx('div', {
          className: 'p-6 max-w-xl mx-auto',
          children: c.jsxs('div', {
            className: 'rounded-lg border border-red-200 bg-red-50 p-6 space-y-4',
            role: 'alert',
            children: [
              c.jsx('h2', {
                className: 'text-lg font-semibold text-red-800',
                children: 'Something went wrong in the dashboard',
              }),
              c.jsx('p', {
                className: 'text-sm text-red-700',
                children:
                  'Try refreshing the page. If the issue persists, capture the console logs and notify the engineering team.',
              }),
              this.state.errorMessage &&
                c.jsxs('p', {
                  className: 'text-xs text-red-600',
                  children: ['Details: ', this.state.errorMessage],
                }),
              c.jsxs('div', {
                className: 'flex gap-3',
                children: [
                  c.jsx('button', {
                    type: 'button',
                    onClick: this.handleReset,
                    className:
                      'rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700',
                    children: 'Try again',
                  }),
                  c.jsx('button', {
                    type: 'button',
                    onClick: () => window.location.reload(),
                    className:
                      'rounded border border-red-600 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100',
                    children: 'Reload',
                  }),
                ],
              }),
            ],
          }),
        })
      : this.props.children;
  }
}
function ew() {
  return c.jsx(Jx, { children: c.jsx(Xx, {}) });
}
var nl = (e) => e.type === 'checkbox',
  Sr = (e) => e instanceof Date,
  it = (e) => e == null;
const Jm = (e) => typeof e == 'object';
var Me = (e) => !it(e) && !Array.isArray(e) && Jm(e) && !Sr(e),
  tw = (e) => (Me(e) && e.target ? (nl(e.target) ? e.target.checked : e.target.value) : e),
  nw = (e) => e.substring(0, e.search(/\.\d+(\.|$)/)) || e,
  rw = (e, t) => e.has(nw(t)),
  sw = (e) => {
    const t = e.constructor && e.constructor.prototype;
    return Me(t) && t.hasOwnProperty('isPrototypeOf');
  },
  Dc = typeof window < 'u' && typeof window.HTMLElement < 'u' && typeof document < 'u';
function $e(e) {
  let t;
  const n = Array.isArray(e),
    r = typeof FileList < 'u' ? e instanceof FileList : !1;
  if (e instanceof Date) t = new Date(e);
  else if (!(Dc && (e instanceof Blob || r)) && (n || Me(e)))
    if (((t = n ? [] : Object.create(Object.getPrototypeOf(e))), !n && !sw(e))) t = e;
    else for (const s in e) e.hasOwnProperty(s) && (t[s] = $e(e[s]));
  else return e;
  return t;
}
var Ua = (e) => /^\w*$/.test(e),
  Fe = (e) => e === void 0,
  zc = (e) => (Array.isArray(e) ? e.filter(Boolean) : []),
  Uc = (e) => zc(e.replace(/["|']|\]/g, '').split(/\.|\[/)),
  $ = (e, t, n) => {
    if (!t || !Me(e)) return n;
    const r = (Ua(t) ? [t] : Uc(t)).reduce((s, i) => (it(s) ? s : s[i]), e);
    return Fe(r) || r === e ? (Fe(e[t]) ? n : e[t]) : r;
  },
  Xt = (e) => typeof e == 'boolean',
  ye = (e, t, n) => {
    let r = -1;
    const s = Ua(t) ? [t] : Uc(t),
      i = s.length,
      l = i - 1;
    for (; ++r < i; ) {
      const a = s[r];
      let o = n;
      if (r !== l) {
        const u = e[a];
        o = Me(u) || Array.isArray(u) ? u : isNaN(+s[r + 1]) ? {} : [];
      }
      if (a === '__proto__' || a === 'constructor' || a === 'prototype') return;
      ((e[a] = o), (e = e[a]));
    }
  };
const kf = { BLUR: 'blur', FOCUS_OUT: 'focusout' },
  Bt = {
    onBlur: 'onBlur',
    onChange: 'onChange',
    onSubmit: 'onSubmit',
    onTouched: 'onTouched',
    all: 'all',
  },
  un = {
    max: 'max',
    min: 'min',
    maxLength: 'maxLength',
    minLength: 'minLength',
    pattern: 'pattern',
    required: 'required',
    validate: 'validate',
  },
  iw = Xe.createContext(null);
iw.displayName = 'HookFormContext';
var lw = (e, t, n, r = !0) => {
  const s = { defaultValues: t._defaultValues };
  for (const i in e)
    Object.defineProperty(s, i, {
      get: () => {
        const l = i;
        return (t._proxyFormState[l] !== Bt.all && (t._proxyFormState[l] = !r || Bt.all), e[l]);
      },
    });
  return s;
};
const aw = typeof window < 'u' ? Xe.useLayoutEffect : Xe.useEffect;
var gt = (e) => typeof e == 'string',
  ow = (e, t, n, r, s) =>
    gt(e)
      ? (r && t.watch.add(e), $(n, e, s))
      : Array.isArray(e)
        ? e.map((i) => (r && t.watch.add(i), $(n, i)))
        : (r && (t.watchAll = !0), n),
  Pu = (e) => it(e) || !Jm(e);
function Mn(e, t, n = new WeakSet()) {
  if (Pu(e) || Pu(t)) return e === t;
  if (Sr(e) && Sr(t)) return e.getTime() === t.getTime();
  const r = Object.keys(e),
    s = Object.keys(t);
  if (r.length !== s.length) return !1;
  if (n.has(e) || n.has(t)) return !0;
  (n.add(e), n.add(t));
  for (const i of r) {
    const l = e[i];
    if (!s.includes(i)) return !1;
    if (i !== 'ref') {
      const a = t[i];
      if (
        (Sr(l) && Sr(a)) || (Me(l) && Me(a)) || (Array.isArray(l) && Array.isArray(a))
          ? !Mn(l, a, n)
          : l !== a
      )
        return !1;
    }
  }
  return !0;
}
var ey = (e, t, n, r, s) =>
    t ? { ...n[e], types: { ...(n[e] && n[e].types ? n[e].types : {}), [r]: s || !0 } } : {},
  wi = (e) => (Array.isArray(e) ? e : [e]),
  Sf = () => {
    let e = [];
    return {
      get observers() {
        return e;
      },
      next: (s) => {
        for (const i of e) i.next && i.next(s);
      },
      subscribe: (s) => (
        e.push(s),
        {
          unsubscribe: () => {
            e = e.filter((i) => i !== s);
          },
        }
      ),
      unsubscribe: () => {
        e = [];
      },
    };
  };
function ty(e, t) {
  const n = {};
  for (const r in e)
    if (e.hasOwnProperty(r)) {
      const s = e[r],
        i = t[r];
      if (s && Me(s) && i) {
        const l = ty(s, i);
        Me(l) && (n[r] = l);
      } else e[r] && (n[r] = i);
    }
  return n;
}
var dt = (e) => Me(e) && !Object.keys(e).length,
  Vc = (e) => e.type === 'file',
  Qt = (e) => typeof e == 'function',
  ha = (e) => {
    if (!Dc) return !1;
    const t = e ? e.ownerDocument : 0;
    return e instanceof (t && t.defaultView ? t.defaultView.HTMLElement : HTMLElement);
  },
  ny = (e) => e.type === 'select-multiple',
  $c = (e) => e.type === 'radio',
  uw = (e) => $c(e) || nl(e),
  go = (e) => ha(e) && e.isConnected;
function cw(e, t) {
  const n = t.slice(0, -1).length;
  let r = 0;
  for (; r < n; ) e = Fe(e) ? r++ : e[t[r++]];
  return e;
}
function dw(e) {
  for (const t in e) if (e.hasOwnProperty(t) && !Fe(e[t])) return !1;
  return !0;
}
function Ae(e, t) {
  const n = Array.isArray(t) ? t : Ua(t) ? [t] : Uc(t),
    r = n.length === 1 ? e : cw(e, n),
    s = n.length - 1,
    i = n[s];
  return (
    r && delete r[i],
    s !== 0 && ((Me(r) && dt(r)) || (Array.isArray(r) && dw(r))) && Ae(e, n.slice(0, -1)),
    e
  );
}
var fw = (e) => {
  for (const t in e) if (Qt(e[t])) return !0;
  return !1;
};
function ry(e) {
  return Array.isArray(e) || (Me(e) && !fw(e));
}
function bu(e, t = {}) {
  for (const n in e)
    ry(e[n]) ? ((t[n] = Array.isArray(e[n]) ? [] : {}), bu(e[n], t[n])) : it(e[n]) || (t[n] = !0);
  return t;
}
function Gr(e, t, n) {
  n || (n = bu(t));
  for (const r in e)
    ry(e[r])
      ? Fe(t) || Pu(n[r])
        ? (n[r] = bu(e[r], Array.isArray(e[r]) ? [] : {}))
        : Gr(e[r], it(t) ? {} : t[r], n[r])
      : (n[r] = !Mn(e[r], t[r]));
  return n;
}
const Cf = { value: !1, isValid: !1 },
  Ef = { value: !0, isValid: !0 };
var sy = (e) => {
    if (Array.isArray(e)) {
      if (e.length > 1) {
        const t = e.filter((n) => n && n.checked && !n.disabled).map((n) => n.value);
        return { value: t, isValid: !!t.length };
      }
      return e[0].checked && !e[0].disabled
        ? e[0].attributes && !Fe(e[0].attributes.value)
          ? Fe(e[0].value) || e[0].value === ''
            ? Ef
            : { value: e[0].value, isValid: !0 }
          : Ef
        : Cf;
    }
    return Cf;
  },
  iy = (e, { valueAsNumber: t, valueAsDate: n, setValueAs: r }) =>
    Fe(e) ? e : t ? (e === '' ? NaN : e && +e) : n && gt(e) ? new Date(e) : r ? r(e) : e;
const Nf = { isValid: !1, value: null };
var ly = (e) =>
  Array.isArray(e)
    ? e.reduce((t, n) => (n && n.checked && !n.disabled ? { isValid: !0, value: n.value } : t), Nf)
    : Nf;
function jf(e) {
  const t = e.ref;
  return Vc(t)
    ? t.files
    : $c(t)
      ? ly(e.refs).value
      : ny(t)
        ? [...t.selectedOptions].map(({ value: n }) => n)
        : nl(t)
          ? sy(e.refs).value
          : iy(Fe(t.value) ? e.ref.value : t.value, e);
}
var hw = (e, t, n, r) => {
    const s = {};
    for (const i of e) {
      const l = $(t, i);
      l && ye(s, i, l._f);
    }
    return { criteriaMode: n, names: [...e], fields: s, shouldUseNativeValidation: r };
  },
  pa = (e) => e instanceof RegExp,
  ri = (e) => (Fe(e) ? e : pa(e) ? e.source : Me(e) ? (pa(e.value) ? e.value.source : e.value) : e),
  Rf = (e) => ({
    isOnSubmit: !e || e === Bt.onSubmit,
    isOnBlur: e === Bt.onBlur,
    isOnChange: e === Bt.onChange,
    isOnAll: e === Bt.all,
    isOnTouch: e === Bt.onTouched,
  });
const Tf = 'AsyncFunction';
var pw = (e) =>
    !!e &&
    !!e.validate &&
    !!(
      (Qt(e.validate) && e.validate.constructor.name === Tf) ||
      (Me(e.validate) && Object.values(e.validate).find((t) => t.constructor.name === Tf))
    ),
  mw = (e) =>
    e.mount &&
    (e.required || e.min || e.max || e.maxLength || e.minLength || e.pattern || e.validate),
  Of = (e, t, n) =>
    !n &&
    (t.watchAll ||
      t.watch.has(e) ||
      [...t.watch].some((r) => e.startsWith(r) && /^\.\w+/.test(e.slice(r.length))));
const _i = (e, t, n, r) => {
  for (const s of n || Object.keys(e)) {
    const i = $(e, s);
    if (i) {
      const { _f: l, ...a } = i;
      if (l) {
        if (l.refs && l.refs[0] && t(l.refs[0], s) && !r) return !0;
        if (l.ref && t(l.ref, l.name) && !r) return !0;
        if (_i(a, t)) break;
      } else if (Me(a) && _i(a, t)) break;
    }
  }
};
function Pf(e, t, n) {
  const r = $(e, n);
  if (r || Ua(n)) return { error: r, name: n };
  const s = n.split('.');
  for (; s.length; ) {
    const i = s.join('.'),
      l = $(t, i),
      a = $(e, i);
    if (l && !Array.isArray(l) && n !== i) return { name: n };
    if (a && a.type) return { name: i, error: a };
    if (a && a.root && a.root.type) return { name: `${i}.root`, error: a.root };
    s.pop();
  }
  return { name: n };
}
var yw = (e, t, n, r) => {
    n(e);
    const { name: s, ...i } = e;
    return (
      dt(i) ||
      Object.keys(i).length >= Object.keys(t).length ||
      Object.keys(i).find((l) => t[l] === (!r || Bt.all))
    );
  },
  vw = (e, t, n) =>
    !e ||
    !t ||
    e === t ||
    wi(e).some((r) => r && (n ? r === t : r.startsWith(t) || t.startsWith(r))),
  gw = (e, t, n, r, s) =>
    s.isOnAll
      ? !1
      : !n && s.isOnTouch
        ? !(t || e)
        : (n ? r.isOnBlur : s.isOnBlur)
          ? !e
          : (n ? r.isOnChange : s.isOnChange)
            ? e
            : !0,
  xw = (e, t) => !zc($(e, t)).length && Ae(e, t),
  ww = (e, t, n) => {
    const r = wi($(e, n));
    return (ye(r, 'root', t[n]), ye(e, n, r), e);
  };
function bf(e, t, n = 'validate') {
  if (gt(e) || (Array.isArray(e) && e.every(gt)) || (Xt(e) && !e))
    return { type: n, message: gt(e) ? e : '', ref: t };
}
var qr = (e) => (Me(e) && !pa(e) ? e : { value: e, message: '' }),
  Af = async (e, t, n, r, s, i) => {
    const {
        ref: l,
        refs: a,
        required: o,
        maxLength: u,
        minLength: f,
        min: h,
        max: p,
        pattern: k,
        validate: S,
        name: _,
        valueAsNumber: N,
        mount: y,
      } = e._f,
      d = $(n, _);
    if (!y || t.has(_)) return {};
    const m = a ? a[0] : l,
      x = (G) => {
        s && m.reportValidity && (m.setCustomValidity(Xt(G) ? '' : G || ''), m.reportValidity());
      },
      j = {},
      O = $c(l),
      A = nl(l),
      L = O || A,
      q =
        ((N || Vc(l)) && Fe(l.value) && Fe(d)) ||
        (ha(l) && l.value === '') ||
        d === '' ||
        (Array.isArray(d) && !d.length),
      P = ey.bind(null, _, r, j),
      H = (G, ee, ve, ae = un.maxLength, ie = un.minLength) => {
        const qe = G ? ee : ve;
        j[_] = { type: G ? ae : ie, message: qe, ref: l, ...P(G ? ae : ie, qe) };
      };
    if (
      i
        ? !Array.isArray(d) || !d.length
        : o &&
          ((!L && (q || it(d))) || (Xt(d) && !d) || (A && !sy(a).isValid) || (O && !ly(a).isValid))
    ) {
      const { value: G, message: ee } = gt(o) ? { value: !!o, message: o } : qr(o);
      if (G && ((j[_] = { type: un.required, message: ee, ref: m, ...P(un.required, ee) }), !r))
        return (x(ee), j);
    }
    if (!q && (!it(h) || !it(p))) {
      let G, ee;
      const ve = qr(p),
        ae = qr(h);
      if (!it(d) && !isNaN(d)) {
        const ie = l.valueAsNumber || (d && +d);
        (it(ve.value) || (G = ie > ve.value), it(ae.value) || (ee = ie < ae.value));
      } else {
        const ie = l.valueAsDate || new Date(d),
          qe = (Y) => new Date(new Date().toDateString() + ' ' + Y),
          D = l.type == 'time',
          K = l.type == 'week';
        (gt(ve.value) &&
          d &&
          (G = D ? qe(d) > qe(ve.value) : K ? d > ve.value : ie > new Date(ve.value)),
          gt(ae.value) &&
            d &&
            (ee = D ? qe(d) < qe(ae.value) : K ? d < ae.value : ie < new Date(ae.value)));
      }
      if ((G || ee) && (H(!!G, ve.message, ae.message, un.max, un.min), !r))
        return (x(j[_].message), j);
    }
    if ((u || f) && !q && (gt(d) || (i && Array.isArray(d)))) {
      const G = qr(u),
        ee = qr(f),
        ve = !it(G.value) && d.length > +G.value,
        ae = !it(ee.value) && d.length < +ee.value;
      if ((ve || ae) && (H(ve, G.message, ee.message), !r)) return (x(j[_].message), j);
    }
    if (k && !q && gt(d)) {
      const { value: G, message: ee } = qr(k);
      if (
        pa(G) &&
        !d.match(G) &&
        ((j[_] = { type: un.pattern, message: ee, ref: l, ...P(un.pattern, ee) }), !r)
      )
        return (x(ee), j);
    }
    if (S) {
      if (Qt(S)) {
        const G = await S(d, n),
          ee = bf(G, m);
        if (ee && ((j[_] = { ...ee, ...P(un.validate, ee.message) }), !r))
          return (x(ee.message), j);
      } else if (Me(S)) {
        let G = {};
        for (const ee in S) {
          if (!dt(G) && !r) break;
          const ve = bf(await S[ee](d, n), m, ee);
          ve && ((G = { ...ve, ...P(ee, ve.message) }), x(ve.message), r && (j[_] = G));
        }
        if (!dt(G) && ((j[_] = { ref: m, ...G }), !r)) return j;
      }
    }
    return (x(!0), j);
  };
const _w = { mode: Bt.onSubmit, reValidateMode: Bt.onChange, shouldFocusError: !0 };
function kw(e = {}) {
  let t = { ..._w, ...e },
    n = {
      submitCount: 0,
      isDirty: !1,
      isReady: !1,
      isLoading: Qt(t.defaultValues),
      isValidating: !1,
      isSubmitted: !1,
      isSubmitting: !1,
      isSubmitSuccessful: !1,
      isValid: !1,
      touchedFields: {},
      dirtyFields: {},
      validatingFields: {},
      errors: t.errors || {},
      disabled: t.disabled || !1,
    },
    r = {},
    s = Me(t.defaultValues) || Me(t.values) ? $e(t.defaultValues || t.values) || {} : {},
    i = t.shouldUnregister ? {} : $e(s),
    l = { action: !1, mount: !1, watch: !1 },
    a = {
      mount: new Set(),
      disabled: new Set(),
      unMount: new Set(),
      array: new Set(),
      watch: new Set(),
    },
    o,
    u = 0;
  const f = {
    isDirty: !1,
    dirtyFields: !1,
    validatingFields: !1,
    touchedFields: !1,
    isValidating: !1,
    isValid: !1,
    errors: !1,
  };
  let h = { ...f };
  const p = { array: Sf(), state: Sf() },
    k = t.criteriaMode === Bt.all,
    S = (g) => (w) => {
      (clearTimeout(u), (u = setTimeout(g, w)));
    },
    _ = async (g) => {
      if (!t.disabled && (f.isValid || h.isValid || g)) {
        const w = t.resolver ? dt((await A()).errors) : await q(r, !0);
        w !== n.isValid && p.state.next({ isValid: w });
      }
    },
    N = (g, w) => {
      !t.disabled &&
        (f.isValidating || f.validatingFields || h.isValidating || h.validatingFields) &&
        ((g || Array.from(a.mount)).forEach((C) => {
          C && (w ? ye(n.validatingFields, C, w) : Ae(n.validatingFields, C));
        }),
        p.state.next({
          validatingFields: n.validatingFields,
          isValidating: !dt(n.validatingFields),
        }));
    },
    y = (g, w = [], C, U, I = !0, b = !0) => {
      if (U && C && !t.disabled) {
        if (((l.action = !0), b && Array.isArray($(r, g)))) {
          const Z = C($(r, g), U.argA, U.argB);
          I && ye(r, g, Z);
        }
        if (b && Array.isArray($(n.errors, g))) {
          const Z = C($(n.errors, g), U.argA, U.argB);
          (I && ye(n.errors, g, Z), xw(n.errors, g));
        }
        if ((f.touchedFields || h.touchedFields) && b && Array.isArray($(n.touchedFields, g))) {
          const Z = C($(n.touchedFields, g), U.argA, U.argB);
          I && ye(n.touchedFields, g, Z);
        }
        ((f.dirtyFields || h.dirtyFields) && (n.dirtyFields = Gr(s, i)),
          p.state.next({
            name: g,
            isDirty: H(g, w),
            dirtyFields: n.dirtyFields,
            errors: n.errors,
            isValid: n.isValid,
          }));
      } else ye(i, g, w);
    },
    d = (g, w) => {
      (ye(n.errors, g, w), p.state.next({ errors: n.errors }));
    },
    m = (g) => {
      ((n.errors = g), p.state.next({ errors: n.errors, isValid: !1 }));
    },
    x = (g, w, C, U) => {
      const I = $(r, g);
      if (I) {
        const b = $(i, g, Fe(C) ? $(s, g) : C);
        (Fe(b) || (U && U.defaultChecked) || w ? ye(i, g, w ? b : jf(I._f)) : ve(g, b),
          l.mount && _());
      }
    },
    j = (g, w, C, U, I) => {
      let b = !1,
        Z = !1;
      const he = { name: g };
      if (!t.disabled) {
        if (!C || U) {
          (f.isDirty || h.isDirty) &&
            ((Z = n.isDirty), (n.isDirty = he.isDirty = H()), (b = Z !== he.isDirty));
          const xe = Mn($(s, g), w);
          ((Z = !!$(n.dirtyFields, g)),
            xe ? Ae(n.dirtyFields, g) : ye(n.dirtyFields, g, !0),
            (he.dirtyFields = n.dirtyFields),
            (b = b || ((f.dirtyFields || h.dirtyFields) && Z !== !xe)));
        }
        if (C) {
          const xe = $(n.touchedFields, g);
          xe ||
            (ye(n.touchedFields, g, C),
            (he.touchedFields = n.touchedFields),
            (b = b || ((f.touchedFields || h.touchedFields) && xe !== C)));
        }
        b && I && p.state.next(he);
      }
      return b ? he : {};
    },
    O = (g, w, C, U) => {
      const I = $(n.errors, g),
        b = (f.isValid || h.isValid) && Xt(w) && n.isValid !== w;
      if (
        (t.delayError && C
          ? ((o = S(() => d(g, C))), o(t.delayError))
          : (clearTimeout(u), (o = null), C ? ye(n.errors, g, C) : Ae(n.errors, g)),
        (C ? !Mn(I, C) : I) || !dt(U) || b)
      ) {
        const Z = { ...U, ...(b && Xt(w) ? { isValid: w } : {}), errors: n.errors, name: g };
        ((n = { ...n, ...Z }), p.state.next(Z));
      }
    },
    A = async (g) => {
      N(g, !0);
      const w = await t.resolver(
        i,
        t.context,
        hw(g || a.mount, r, t.criteriaMode, t.shouldUseNativeValidation),
      );
      return (N(g), w);
    },
    L = async (g) => {
      const { errors: w } = await A(g);
      if (g)
        for (const C of g) {
          const U = $(w, C);
          U ? ye(n.errors, C, U) : Ae(n.errors, C);
        }
      else n.errors = w;
      return w;
    },
    q = async (g, w, C = { valid: !0 }) => {
      for (const U in g) {
        const I = g[U];
        if (I) {
          const { _f: b, ...Z } = I;
          if (b) {
            const he = a.array.has(b.name),
              xe = I._f && pw(I._f);
            xe && f.validatingFields && N([b.name], !0);
            const Nt = await Af(I, a.disabled, i, k, t.shouldUseNativeValidation && !w, he);
            if ((xe && f.validatingFields && N([b.name]), Nt[b.name] && ((C.valid = !1), w))) break;
            !w &&
              ($(Nt, b.name)
                ? he
                  ? ww(n.errors, Nt, b.name)
                  : ye(n.errors, b.name, Nt[b.name])
                : Ae(n.errors, b.name));
          }
          !dt(Z) && (await q(Z, w, C));
        }
      }
      return C.valid;
    },
    P = () => {
      for (const g of a.unMount) {
        const w = $(r, g);
        w && (w._f.refs ? w._f.refs.every((C) => !go(C)) : !go(w._f.ref)) && Kt(g);
      }
      a.unMount = new Set();
    },
    H = (g, w) => !t.disabled && (g && w && ye(i, g, w), !Mn(Y(), s)),
    G = (g, w, C) => ow(g, a, { ...(l.mount ? i : Fe(w) ? s : gt(g) ? { [g]: w } : w) }, C, w),
    ee = (g) => zc($(l.mount ? i : s, g, t.shouldUnregister ? $(s, g, []) : [])),
    ve = (g, w, C = {}) => {
      const U = $(r, g);
      let I = w;
      if (U) {
        const b = U._f;
        b &&
          (!b.disabled && ye(i, g, iy(w, b)),
          (I = ha(b.ref) && it(w) ? '' : w),
          ny(b.ref)
            ? [...b.ref.options].forEach((Z) => (Z.selected = I.includes(Z.value)))
            : b.refs
              ? nl(b.ref)
                ? b.refs.forEach((Z) => {
                    (!Z.defaultChecked || !Z.disabled) &&
                      (Array.isArray(I)
                        ? (Z.checked = !!I.find((he) => he === Z.value))
                        : (Z.checked = I === Z.value || !!I));
                  })
                : b.refs.forEach((Z) => (Z.checked = Z.value === I))
              : Vc(b.ref)
                ? (b.ref.value = '')
                : ((b.ref.value = I), b.ref.type || p.state.next({ name: g, values: $e(i) })));
      }
      ((C.shouldDirty || C.shouldTouch) && j(g, I, C.shouldTouch, C.shouldDirty, !0),
        C.shouldValidate && K(g));
    },
    ae = (g, w, C) => {
      for (const U in w) {
        if (!w.hasOwnProperty(U)) return;
        const I = w[U],
          b = g + '.' + U,
          Z = $(r, b);
        (a.array.has(g) || Me(I) || (Z && !Z._f)) && !Sr(I) ? ae(b, I, C) : ve(b, I, C);
      }
    },
    ie = (g, w, C = {}) => {
      const U = $(r, g),
        I = a.array.has(g),
        b = $e(w);
      (ye(i, g, b),
        I
          ? (p.array.next({ name: g, values: $e(i) }),
            (f.isDirty || f.dirtyFields || h.isDirty || h.dirtyFields) &&
              C.shouldDirty &&
              p.state.next({ name: g, dirtyFields: Gr(s, i), isDirty: H(g, b) }))
          : U && !U._f && !it(b)
            ? ae(g, b, C)
            : ve(g, b, C),
        Of(g, a) && p.state.next({ ...n, name: g }),
        p.state.next({ name: l.mount ? g : void 0, values: $e(i) }));
    },
    qe = async (g) => {
      l.mount = !0;
      const w = g.target;
      let C = w.name,
        U = !0;
      const I = $(r, C),
        b = (xe) => {
          U = Number.isNaN(xe) || (Sr(xe) && isNaN(xe.getTime())) || Mn(xe, $(i, C, xe));
        },
        Z = Rf(t.mode),
        he = Rf(t.reValidateMode);
      if (I) {
        let xe, Nt;
        const il = w.type ? jf(I._f) : tw(g),
          Rn = g.type === kf.BLUR || g.type === kf.FOCUS_OUT,
          hy =
            (!mw(I._f) && !t.resolver && !$(n.errors, C) && !I._f.deps) ||
            gw(Rn, $(n.touchedFields, C), n.isSubmitted, he, Z),
          Va = Of(C, a, Rn);
        (ye(i, C, il),
          Rn
            ? (!w || !w.readOnly) && (I._f.onBlur && I._f.onBlur(g), o && o(0))
            : I._f.onChange && I._f.onChange(g));
        const $a = j(C, il, Rn),
          py = !dt($a) || Va;
        if ((!Rn && p.state.next({ name: C, type: g.type, values: $e(i) }), hy))
          return (
            (f.isValid || h.isValid) && (t.mode === 'onBlur' ? Rn && _() : Rn || _()),
            py && p.state.next({ name: C, ...(Va ? {} : $a) })
          );
        if ((!Rn && Va && p.state.next({ ...n }), t.resolver)) {
          const { errors: Wc } = await A([C]);
          if ((b(il), U)) {
            const my = Pf(n.errors, r, C),
              Zc = Pf(Wc, r, my.name || C);
            ((xe = Zc.error), (C = Zc.name), (Nt = dt(Wc)));
          }
        } else
          (N([C], !0),
            (xe = (await Af(I, a.disabled, i, k, t.shouldUseNativeValidation))[C]),
            N([C]),
            b(il),
            U && (xe ? (Nt = !1) : (f.isValid || h.isValid) && (Nt = await q(r, !0))));
        U &&
          (I._f.deps && (!Array.isArray(I._f.deps) || I._f.deps.length > 0) && K(I._f.deps),
          O(C, Nt, xe, $a));
      }
    },
    D = (g, w) => {
      if ($(n.errors, w) && g.focus) return (g.focus(), 1);
    },
    K = async (g, w = {}) => {
      let C, U;
      const I = wi(g);
      if (t.resolver) {
        const b = await L(Fe(g) ? g : I);
        ((C = dt(b)), (U = g ? !I.some((Z) => $(b, Z)) : C));
      } else
        g
          ? ((U = (
              await Promise.all(
                I.map(async (b) => {
                  const Z = $(r, b);
                  return await q(Z && Z._f ? { [b]: Z } : Z);
                }),
              )
            ).every(Boolean)),
            !(!U && !n.isValid) && _())
          : (U = C = await q(r));
      return (
        p.state.next({
          ...(!gt(g) || ((f.isValid || h.isValid) && C !== n.isValid) ? {} : { name: g }),
          ...(t.resolver || !g ? { isValid: C } : {}),
          errors: n.errors,
        }),
        w.shouldFocus && !U && _i(r, D, g ? I : a.mount),
        U
      );
    },
    Y = (g, w) => {
      let C = { ...(l.mount ? i : s) };
      return (
        w && (C = ty(w.dirtyFields ? n.dirtyFields : n.touchedFields, C)),
        Fe(g) ? C : gt(g) ? $(C, g) : g.map((U) => $(C, U))
      );
    },
    ge = (g, w) => ({
      invalid: !!$((w || n).errors, g),
      isDirty: !!$((w || n).dirtyFields, g),
      error: $((w || n).errors, g),
      isValidating: !!$(n.validatingFields, g),
      isTouched: !!$((w || n).touchedFields, g),
    }),
    Re = (g) => {
      (g && wi(g).forEach((w) => Ae(n.errors, w)), p.state.next({ errors: g ? n.errors : {} }));
    },
    an = (g, w, C) => {
      const U = ($(r, g, { _f: {} })._f || {}).ref,
        I = $(n.errors, g) || {},
        { ref: b, message: Z, type: he, ...xe } = I;
      (ye(n.errors, g, { ...xe, ...w, ref: U }),
        p.state.next({ name: g, errors: n.errors, isValid: !1 }),
        C && C.shouldFocus && U && U.focus && U.focus());
    },
    Et = (g, w) =>
      Qt(g) ? p.state.subscribe({ next: (C) => 'values' in C && g(G(void 0, w), C) }) : G(g, w, !0),
    on = (g) =>
      p.state.subscribe({
        next: (w) => {
          vw(g.name, w.name, g.exact) &&
            yw(w, g.formState || f, Zr, g.reRenderRoot) &&
            g.callback({ values: { ...i }, ...n, ...w, defaultValues: s });
        },
      }).unsubscribe,
    It = (g) => ((l.mount = !0), (h = { ...h, ...g.formState }), on({ ...g, formState: h })),
    Kt = (g, w = {}) => {
      for (const C of g ? wi(g) : a.mount)
        (a.mount.delete(C),
          a.array.delete(C),
          w.keepValue || (Ae(r, C), Ae(i, C)),
          !w.keepError && Ae(n.errors, C),
          !w.keepDirty && Ae(n.dirtyFields, C),
          !w.keepTouched && Ae(n.touchedFields, C),
          !w.keepIsValidating && Ae(n.validatingFields, C),
          !t.shouldUnregister && !w.keepDefaultValue && Ae(s, C));
      (p.state.next({ values: $e(i) }),
        p.state.next({ ...n, ...(w.keepDirty ? { isDirty: H() } : {}) }),
        !w.keepIsValid && _());
    },
    rl = ({ disabled: g, name: w }) => {
      ((Xt(g) && l.mount) || g || a.disabled.has(w)) &&
        (g ? a.disabled.add(w) : a.disabled.delete(w));
    },
    Zs = (g, w = {}) => {
      let C = $(r, g);
      const U = Xt(w.disabled) || Xt(t.disabled);
      return (
        ye(r, g, {
          ...(C || {}),
          _f: { ...(C && C._f ? C._f : { ref: { name: g } }), name: g, mount: !0, ...w },
        }),
        a.mount.add(g),
        C ? rl({ disabled: Xt(w.disabled) ? w.disabled : t.disabled, name: g }) : x(g, !0, w.value),
        {
          ...(U ? { disabled: w.disabled || t.disabled } : {}),
          ...(t.progressive
            ? {
                required: !!w.required,
                min: ri(w.min),
                max: ri(w.max),
                minLength: ri(w.minLength),
                maxLength: ri(w.maxLength),
                pattern: ri(w.pattern),
              }
            : {}),
          name: g,
          onChange: qe,
          onBlur: qe,
          ref: (I) => {
            if (I) {
              (Zs(g, w), (C = $(r, g)));
              const b =
                  (Fe(I.value) &&
                    I.querySelectorAll &&
                    I.querySelectorAll('input,select,textarea')[0]) ||
                  I,
                Z = uw(b),
                he = C._f.refs || [];
              if (Z ? he.find((xe) => xe === b) : b === C._f.ref) return;
              (ye(r, g, {
                _f: {
                  ...C._f,
                  ...(Z
                    ? {
                        refs: [...he.filter(go), b, ...(Array.isArray($(s, g)) ? [{}] : [])],
                        ref: { type: b.type, name: g },
                      }
                    : { ref: b }),
                },
              }),
                x(g, !1, void 0, b));
            } else
              ((C = $(r, g, {})),
                C._f && (C._f.mount = !1),
                (t.shouldUnregister || w.shouldUnregister) &&
                  !(rw(a.array, g) && l.action) &&
                  a.unMount.add(g));
          },
        }
      );
    },
    F = () => t.shouldFocusError && _i(r, D, a.mount),
    te = (g) => {
      Xt(g) &&
        (p.state.next({ disabled: g }),
        _i(
          r,
          (w, C) => {
            const U = $(r, C);
            U &&
              ((w.disabled = U._f.disabled || g),
              Array.isArray(U._f.refs) &&
                U._f.refs.forEach((I) => {
                  I.disabled = U._f.disabled || g;
                }));
          },
          0,
          !1,
        ));
    },
    fe = (g, w) => async (C) => {
      let U;
      C && (C.preventDefault && C.preventDefault(), C.persist && C.persist());
      let I = $e(i);
      if ((p.state.next({ isSubmitting: !0 }), t.resolver)) {
        const { errors: b, values: Z } = await A();
        ((n.errors = b), (I = $e(Z)));
      } else await q(r);
      if (a.disabled.size) for (const b of a.disabled) Ae(I, b);
      if ((Ae(n.errors, 'root'), dt(n.errors))) {
        p.state.next({ errors: {} });
        try {
          await g(I, C);
        } catch (b) {
          U = b;
        }
      } else (w && (await w({ ...n.errors }, C)), F(), setTimeout(F));
      if (
        (p.state.next({
          isSubmitted: !0,
          isSubmitting: !1,
          isSubmitSuccessful: dt(n.errors) && !U,
          submitCount: n.submitCount + 1,
          errors: n.errors,
        }),
        U)
      )
        throw U;
    },
    Ce = (g, w = {}) => {
      $(r, g) &&
        (Fe(w.defaultValue)
          ? ie(g, $e($(s, g)))
          : (ie(g, w.defaultValue), ye(s, g, $e(w.defaultValue))),
        w.keepTouched || Ae(n.touchedFields, g),
        w.keepDirty ||
          (Ae(n.dirtyFields, g), (n.isDirty = w.defaultValue ? H(g, $e($(s, g))) : H())),
        w.keepError || (Ae(n.errors, g), f.isValid && _()),
        p.state.next({ ...n }));
    },
    me = (g, w = {}) => {
      const C = g ? $e(g) : s,
        U = $e(C),
        I = dt(g),
        b = I ? s : U;
      if ((w.keepDefaultValues || (s = C), !w.keepValues)) {
        if (w.keepDirtyValues) {
          const Z = new Set([...a.mount, ...Object.keys(Gr(s, i))]);
          for (const he of Array.from(Z))
            $(n.dirtyFields, he) ? ye(b, he, $(i, he)) : ie(he, $(b, he));
        } else {
          if (Dc && Fe(g))
            for (const Z of a.mount) {
              const he = $(r, Z);
              if (he && he._f) {
                const xe = Array.isArray(he._f.refs) ? he._f.refs[0] : he._f.ref;
                if (ha(xe)) {
                  const Nt = xe.closest('form');
                  if (Nt) {
                    Nt.reset();
                    break;
                  }
                }
              }
            }
          if (w.keepFieldsRef) for (const Z of a.mount) ie(Z, $(b, Z));
          else r = {};
        }
        ((i = t.shouldUnregister ? (w.keepDefaultValues ? $e(s) : {}) : $e(b)),
          p.array.next({ values: { ...b } }),
          p.state.next({ values: { ...b } }));
      }
      ((a = {
        mount: w.keepDirtyValues ? a.mount : new Set(),
        unMount: new Set(),
        array: new Set(),
        disabled: new Set(),
        watch: new Set(),
        watchAll: !1,
        focus: '',
      }),
        (l.mount = !f.isValid || !!w.keepIsValid || !!w.keepDirtyValues),
        (l.watch = !!t.shouldUnregister),
        p.state.next({
          submitCount: w.keepSubmitCount ? n.submitCount : 0,
          isDirty: I ? !1 : w.keepDirty ? n.isDirty : !!(w.keepDefaultValues && !Mn(g, s)),
          isSubmitted: w.keepIsSubmitted ? n.isSubmitted : !1,
          dirtyFields: I
            ? {}
            : w.keepDirtyValues
              ? w.keepDefaultValues && i
                ? Gr(s, i)
                : n.dirtyFields
              : w.keepDefaultValues && g
                ? Gr(s, g)
                : w.keepDirty
                  ? n.dirtyFields
                  : {},
          touchedFields: w.keepTouched ? n.touchedFields : {},
          errors: w.keepErrors ? n.errors : {},
          isSubmitSuccessful: w.keepIsSubmitSuccessful ? n.isSubmitSuccessful : !1,
          isSubmitting: !1,
          defaultValues: s,
        }));
    },
    Ve = (g, w) => me(Qt(g) ? g(i) : g, w),
    qt = (g, w = {}) => {
      const C = $(r, g),
        U = C && C._f;
      if (U) {
        const I = U.refs ? U.refs[0] : U.ref;
        I.focus && (I.focus(), w.shouldSelect && Qt(I.select) && I.select());
      }
    },
    Zr = (g) => {
      n = { ...n, ...g };
    },
    sl = {
      control: {
        register: Zs,
        unregister: Kt,
        getFieldState: ge,
        handleSubmit: fe,
        setError: an,
        _subscribe: on,
        _runSchema: A,
        _focusError: F,
        _getWatch: G,
        _getDirty: H,
        _setValid: _,
        _setFieldArray: y,
        _setDisabledField: rl,
        _setErrors: m,
        _getFieldArray: ee,
        _reset: me,
        _resetDefaultValues: () =>
          Qt(t.defaultValues) &&
          t.defaultValues().then((g) => {
            (Ve(g, t.resetOptions), p.state.next({ isLoading: !1 }));
          }),
        _removeUnmounted: P,
        _disableForm: te,
        _subjects: p,
        _proxyFormState: f,
        get _fields() {
          return r;
        },
        get _formValues() {
          return i;
        },
        get _state() {
          return l;
        },
        set _state(g) {
          l = g;
        },
        get _defaultValues() {
          return s;
        },
        get _names() {
          return a;
        },
        set _names(g) {
          a = g;
        },
        get _formState() {
          return n;
        },
        get _options() {
          return t;
        },
        set _options(g) {
          t = { ...t, ...g };
        },
      },
      subscribe: It,
      trigger: K,
      register: Zs,
      handleSubmit: fe,
      watch: Et,
      setValue: ie,
      getValues: Y,
      reset: Ve,
      resetField: Ce,
      clearErrors: Re,
      unregister: Kt,
      setError: an,
      setFocus: qt,
      getFieldState: ge,
    };
  return { ...sl, formControl: sl };
}
function Sw(e = {}) {
  const t = Xe.useRef(void 0),
    n = Xe.useRef(void 0),
    [r, s] = Xe.useState({
      isDirty: !1,
      isValidating: !1,
      isLoading: Qt(e.defaultValues),
      isSubmitted: !1,
      isSubmitting: !1,
      isSubmitSuccessful: !1,
      isValid: !1,
      submitCount: 0,
      dirtyFields: {},
      touchedFields: {},
      validatingFields: {},
      errors: e.errors || {},
      disabled: e.disabled || !1,
      isReady: !1,
      defaultValues: Qt(e.defaultValues) ? void 0 : e.defaultValues,
    });
  if (!t.current)
    if (e.formControl)
      ((t.current = { ...e.formControl, formState: r }),
        e.defaultValues &&
          !Qt(e.defaultValues) &&
          e.formControl.reset(e.defaultValues, e.resetOptions));
    else {
      const { formControl: l, ...a } = kw(e);
      t.current = { ...a, formState: r };
    }
  const i = t.current.control;
  return (
    (i._options = e),
    aw(() => {
      const l = i._subscribe({
        formState: i._proxyFormState,
        callback: () => s({ ...i._formState }),
        reRenderRoot: !0,
      });
      return (s((a) => ({ ...a, isReady: !0 })), (i._formState.isReady = !0), l);
    }, [i]),
    Xe.useEffect(() => i._disableForm(e.disabled), [i, e.disabled]),
    Xe.useEffect(() => {
      (e.mode && (i._options.mode = e.mode),
        e.reValidateMode && (i._options.reValidateMode = e.reValidateMode));
    }, [i, e.mode, e.reValidateMode]),
    Xe.useEffect(() => {
      e.errors && (i._setErrors(e.errors), i._focusError());
    }, [i, e.errors]),
    Xe.useEffect(() => {
      e.shouldUnregister && i._subjects.state.next({ values: i._getWatch() });
    }, [i, e.shouldUnregister]),
    Xe.useEffect(() => {
      if (i._proxyFormState.isDirty) {
        const l = i._getDirty();
        l !== r.isDirty && i._subjects.state.next({ isDirty: l });
      }
    }, [i, r.isDirty]),
    Xe.useEffect(() => {
      e.values && !Mn(e.values, n.current)
        ? (i._reset(e.values, { keepFieldsRef: !0, ...i._options.resetOptions }),
          (n.current = e.values),
          s((l) => ({ ...l })))
        : i._resetDefaultValues();
    }, [i, e.values]),
    Xe.useEffect(() => {
      (i._state.mount || (i._setValid(), (i._state.mount = !0)),
        i._state.watch && ((i._state.watch = !1), i._subjects.state.next({ ...i._formState })),
        i._removeUnmounted());
    }),
    (t.current.formState = lw(r, i)),
    t.current
  );
}
var ce;
(function (e) {
  e.assertEqual = (s) => {};
  function t(s) {}
  e.assertIs = t;
  function n(s) {
    throw new Error();
  }
  ((e.assertNever = n),
    (e.arrayToEnum = (s) => {
      const i = {};
      for (const l of s) i[l] = l;
      return i;
    }),
    (e.getValidEnumValues = (s) => {
      const i = e.objectKeys(s).filter((a) => typeof s[s[a]] != 'number'),
        l = {};
      for (const a of i) l[a] = s[a];
      return e.objectValues(l);
    }),
    (e.objectValues = (s) =>
      e.objectKeys(s).map(function (i) {
        return s[i];
      })),
    (e.objectKeys =
      typeof Object.keys == 'function'
        ? (s) => Object.keys(s)
        : (s) => {
            const i = [];
            for (const l in s) Object.prototype.hasOwnProperty.call(s, l) && i.push(l);
            return i;
          }),
    (e.find = (s, i) => {
      for (const l of s) if (i(l)) return l;
    }),
    (e.isInteger =
      typeof Number.isInteger == 'function'
        ? (s) => Number.isInteger(s)
        : (s) => typeof s == 'number' && Number.isFinite(s) && Math.floor(s) === s));
  function r(s, i = ' | ') {
    return s.map((l) => (typeof l == 'string' ? `'${l}'` : l)).join(i);
  }
  ((e.joinValues = r),
    (e.jsonStringifyReplacer = (s, i) => (typeof i == 'bigint' ? i.toString() : i)));
})(ce || (ce = {}));
var Lf;
(function (e) {
  e.mergeShapes = (t, n) => ({ ...t, ...n });
})(Lf || (Lf = {}));
const B = ce.arrayToEnum([
    'string',
    'nan',
    'number',
    'integer',
    'float',
    'boolean',
    'date',
    'bigint',
    'symbol',
    'function',
    'undefined',
    'null',
    'array',
    'object',
    'unknown',
    'promise',
    'void',
    'never',
    'map',
    'set',
  ]),
  Ln = (e) => {
    switch (typeof e) {
      case 'undefined':
        return B.undefined;
      case 'string':
        return B.string;
      case 'number':
        return Number.isNaN(e) ? B.nan : B.number;
      case 'boolean':
        return B.boolean;
      case 'function':
        return B.function;
      case 'bigint':
        return B.bigint;
      case 'symbol':
        return B.symbol;
      case 'object':
        return Array.isArray(e)
          ? B.array
          : e === null
            ? B.null
            : e.then && typeof e.then == 'function' && e.catch && typeof e.catch == 'function'
              ? B.promise
              : typeof Map < 'u' && e instanceof Map
                ? B.map
                : typeof Set < 'u' && e instanceof Set
                  ? B.set
                  : typeof Date < 'u' && e instanceof Date
                    ? B.date
                    : B.object;
      default:
        return B.unknown;
    }
  },
  T = ce.arrayToEnum([
    'invalid_type',
    'invalid_literal',
    'custom',
    'invalid_union',
    'invalid_union_discriminator',
    'invalid_enum_value',
    'unrecognized_keys',
    'invalid_arguments',
    'invalid_return_type',
    'invalid_date',
    'invalid_string',
    'too_small',
    'too_big',
    'invalid_intersection_types',
    'not_multiple_of',
    'not_finite',
  ]);
class En extends Error {
  get errors() {
    return this.issues;
  }
  constructor(t) {
    (super(),
      (this.issues = []),
      (this.addIssue = (r) => {
        this.issues = [...this.issues, r];
      }),
      (this.addIssues = (r = []) => {
        this.issues = [...this.issues, ...r];
      }));
    const n = new.target.prototype;
    (Object.setPrototypeOf ? Object.setPrototypeOf(this, n) : (this.__proto__ = n),
      (this.name = 'ZodError'),
      (this.issues = t));
  }
  format(t) {
    const n =
        t ||
        function (i) {
          return i.message;
        },
      r = { _errors: [] },
      s = (i) => {
        for (const l of i.issues)
          if (l.code === 'invalid_union') l.unionErrors.map(s);
          else if (l.code === 'invalid_return_type') s(l.returnTypeError);
          else if (l.code === 'invalid_arguments') s(l.argumentsError);
          else if (l.path.length === 0) r._errors.push(n(l));
          else {
            let a = r,
              o = 0;
            for (; o < l.path.length; ) {
              const u = l.path[o];
              (o === l.path.length - 1
                ? ((a[u] = a[u] || { _errors: [] }), a[u]._errors.push(n(l)))
                : (a[u] = a[u] || { _errors: [] }),
                (a = a[u]),
                o++);
            }
          }
      };
    return (s(this), r);
  }
  static assert(t) {
    if (!(t instanceof En)) throw new Error(`Not a ZodError: ${t}`);
  }
  toString() {
    return this.message;
  }
  get message() {
    return JSON.stringify(this.issues, ce.jsonStringifyReplacer, 2);
  }
  get isEmpty() {
    return this.issues.length === 0;
  }
  flatten(t = (n) => n.message) {
    const n = {},
      r = [];
    for (const s of this.issues)
      if (s.path.length > 0) {
        const i = s.path[0];
        ((n[i] = n[i] || []), n[i].push(t(s)));
      } else r.push(t(s));
    return { formErrors: r, fieldErrors: n };
  }
  get formErrors() {
    return this.flatten();
  }
}
En.create = (e) => new En(e);
const Au = (e, t) => {
  let n;
  switch (e.code) {
    case T.invalid_type:
      e.received === B.undefined
        ? (n = 'Required')
        : (n = `Expected ${e.expected}, received ${e.received}`);
      break;
    case T.invalid_literal:
      n = `Invalid literal value, expected ${JSON.stringify(e.expected, ce.jsonStringifyReplacer)}`;
      break;
    case T.unrecognized_keys:
      n = `Unrecognized key(s) in object: ${ce.joinValues(e.keys, ', ')}`;
      break;
    case T.invalid_union:
      n = 'Invalid input';
      break;
    case T.invalid_union_discriminator:
      n = `Invalid discriminator value. Expected ${ce.joinValues(e.options)}`;
      break;
    case T.invalid_enum_value:
      n = `Invalid enum value. Expected ${ce.joinValues(e.options)}, received '${e.received}'`;
      break;
    case T.invalid_arguments:
      n = 'Invalid function arguments';
      break;
    case T.invalid_return_type:
      n = 'Invalid function return type';
      break;
    case T.invalid_date:
      n = 'Invalid date';
      break;
    case T.invalid_string:
      typeof e.validation == 'object'
        ? 'includes' in e.validation
          ? ((n = `Invalid input: must include "${e.validation.includes}"`),
            typeof e.validation.position == 'number' &&
              (n = `${n} at one or more positions greater than or equal to ${e.validation.position}`))
          : 'startsWith' in e.validation
            ? (n = `Invalid input: must start with "${e.validation.startsWith}"`)
            : 'endsWith' in e.validation
              ? (n = `Invalid input: must end with "${e.validation.endsWith}"`)
              : ce.assertNever(e.validation)
        : e.validation !== 'regex'
          ? (n = `Invalid ${e.validation}`)
          : (n = 'Invalid');
      break;
    case T.too_small:
      e.type === 'array'
        ? (n = `Array must contain ${e.exact ? 'exactly' : e.inclusive ? 'at least' : 'more than'} ${e.minimum} element(s)`)
        : e.type === 'string'
          ? (n = `String must contain ${e.exact ? 'exactly' : e.inclusive ? 'at least' : 'over'} ${e.minimum} character(s)`)
          : e.type === 'number'
            ? (n = `Number must be ${e.exact ? 'exactly equal to ' : e.inclusive ? 'greater than or equal to ' : 'greater than '}${e.minimum}`)
            : e.type === 'bigint'
              ? (n = `Number must be ${e.exact ? 'exactly equal to ' : e.inclusive ? 'greater than or equal to ' : 'greater than '}${e.minimum}`)
              : e.type === 'date'
                ? (n = `Date must be ${e.exact ? 'exactly equal to ' : e.inclusive ? 'greater than or equal to ' : 'greater than '}${new Date(Number(e.minimum))}`)
                : (n = 'Invalid input');
      break;
    case T.too_big:
      e.type === 'array'
        ? (n = `Array must contain ${e.exact ? 'exactly' : e.inclusive ? 'at most' : 'less than'} ${e.maximum} element(s)`)
        : e.type === 'string'
          ? (n = `String must contain ${e.exact ? 'exactly' : e.inclusive ? 'at most' : 'under'} ${e.maximum} character(s)`)
          : e.type === 'number'
            ? (n = `Number must be ${e.exact ? 'exactly' : e.inclusive ? 'less than or equal to' : 'less than'} ${e.maximum}`)
            : e.type === 'bigint'
              ? (n = `BigInt must be ${e.exact ? 'exactly' : e.inclusive ? 'less than or equal to' : 'less than'} ${e.maximum}`)
              : e.type === 'date'
                ? (n = `Date must be ${e.exact ? 'exactly' : e.inclusive ? 'smaller than or equal to' : 'smaller than'} ${new Date(Number(e.maximum))}`)
                : (n = 'Invalid input');
      break;
    case T.custom:
      n = 'Invalid input';
      break;
    case T.invalid_intersection_types:
      n = 'Intersection results could not be merged';
      break;
    case T.not_multiple_of:
      n = `Number must be a multiple of ${e.multipleOf}`;
      break;
    case T.not_finite:
      n = 'Number must be finite';
      break;
    default:
      ((n = t.defaultError), ce.assertNever(e));
  }
  return { message: n };
};
let Cw = Au;
function Ew() {
  return Cw;
}
const Nw = (e) => {
  const { data: t, path: n, errorMaps: r, issueData: s } = e,
    i = [...n, ...(s.path || [])],
    l = { ...s, path: i };
  if (s.message !== void 0) return { ...s, path: i, message: s.message };
  let a = '';
  const o = r
    .filter((u) => !!u)
    .slice()
    .reverse();
  for (const u of o) a = u(l, { data: t, defaultError: a }).message;
  return { ...s, path: i, message: a };
};
function z(e, t) {
  const n = Ew(),
    r = Nw({
      issueData: t,
      data: e.data,
      path: e.path,
      errorMaps: [e.common.contextualErrorMap, e.schemaErrorMap, n, n === Au ? void 0 : Au].filter(
        (s) => !!s,
      ),
    });
  e.common.issues.push(r);
}
class kt {
  constructor() {
    this.value = 'valid';
  }
  dirty() {
    this.value === 'valid' && (this.value = 'dirty');
  }
  abort() {
    this.value !== 'aborted' && (this.value = 'aborted');
  }
  static mergeArray(t, n) {
    const r = [];
    for (const s of n) {
      if (s.status === 'aborted') return X;
      (s.status === 'dirty' && t.dirty(), r.push(s.value));
    }
    return { status: t.value, value: r };
  }
  static async mergeObjectAsync(t, n) {
    const r = [];
    for (const s of n) {
      const i = await s.key,
        l = await s.value;
      r.push({ key: i, value: l });
    }
    return kt.mergeObjectSync(t, r);
  }
  static mergeObjectSync(t, n) {
    const r = {};
    for (const s of n) {
      const { key: i, value: l } = s;
      if (i.status === 'aborted' || l.status === 'aborted') return X;
      (i.status === 'dirty' && t.dirty(),
        l.status === 'dirty' && t.dirty(),
        i.value !== '__proto__' && (typeof l.value < 'u' || s.alwaysSet) && (r[i.value] = l.value));
    }
    return { status: t.value, value: r };
  }
}
const X = Object.freeze({ status: 'aborted' }),
  ci = (e) => ({ status: 'dirty', value: e }),
  Ft = (e) => ({ status: 'valid', value: e }),
  Ff = (e) => e.status === 'aborted',
  If = (e) => e.status === 'dirty',
  Is = (e) => e.status === 'valid',
  ma = (e) => typeof Promise < 'u' && e instanceof Promise;
var Q;
(function (e) {
  ((e.errToObj = (t) => (typeof t == 'string' ? { message: t } : t || {})),
    (e.toString = (t) => (typeof t == 'string' ? t : t == null ? void 0 : t.message)));
})(Q || (Q = {}));
class cr {
  constructor(t, n, r, s) {
    ((this._cachedPath = []),
      (this.parent = t),
      (this.data = n),
      (this._path = r),
      (this._key = s));
  }
  get path() {
    return (
      this._cachedPath.length ||
        (Array.isArray(this._key)
          ? this._cachedPath.push(...this._path, ...this._key)
          : this._cachedPath.push(...this._path, this._key)),
      this._cachedPath
    );
  }
}
const Mf = (e, t) => {
  if (Is(t)) return { success: !0, data: t.value };
  if (!e.common.issues.length) throw new Error('Validation failed but no issues detected.');
  return {
    success: !1,
    get error() {
      if (this._error) return this._error;
      const n = new En(e.common.issues);
      return ((this._error = n), this._error);
    },
  };
};
function re(e) {
  if (!e) return {};
  const { errorMap: t, invalid_type_error: n, required_error: r, description: s } = e;
  if (t && (n || r))
    throw new Error(
      `Can't use "invalid_type_error" or "required_error" in conjunction with custom error map.`,
    );
  return t
    ? { errorMap: t, description: s }
    : {
        errorMap: (l, a) => {
          const { message: o } = e;
          return l.code === 'invalid_enum_value'
            ? { message: o ?? a.defaultError }
            : typeof a.data > 'u'
              ? { message: o ?? r ?? a.defaultError }
              : l.code !== 'invalid_type'
                ? { message: a.defaultError }
                : { message: o ?? n ?? a.defaultError };
        },
        description: s,
      };
}
class ue {
  get description() {
    return this._def.description;
  }
  _getType(t) {
    return Ln(t.data);
  }
  _getOrReturnCtx(t, n) {
    return (
      n || {
        common: t.parent.common,
        data: t.data,
        parsedType: Ln(t.data),
        schemaErrorMap: this._def.errorMap,
        path: t.path,
        parent: t.parent,
      }
    );
  }
  _processInputParams(t) {
    return {
      status: new kt(),
      ctx: {
        common: t.parent.common,
        data: t.data,
        parsedType: Ln(t.data),
        schemaErrorMap: this._def.errorMap,
        path: t.path,
        parent: t.parent,
      },
    };
  }
  _parseSync(t) {
    const n = this._parse(t);
    if (ma(n)) throw new Error('Synchronous parse encountered promise.');
    return n;
  }
  _parseAsync(t) {
    const n = this._parse(t);
    return Promise.resolve(n);
  }
  parse(t, n) {
    const r = this.safeParse(t, n);
    if (r.success) return r.data;
    throw r.error;
  }
  safeParse(t, n) {
    const r = {
        common: {
          issues: [],
          async: (n == null ? void 0 : n.async) ?? !1,
          contextualErrorMap: n == null ? void 0 : n.errorMap,
        },
        path: (n == null ? void 0 : n.path) || [],
        schemaErrorMap: this._def.errorMap,
        parent: null,
        data: t,
        parsedType: Ln(t),
      },
      s = this._parseSync({ data: t, path: r.path, parent: r });
    return Mf(r, s);
  }
  '~validate'(t) {
    var r, s;
    const n = {
      common: { issues: [], async: !!this['~standard'].async },
      path: [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data: t,
      parsedType: Ln(t),
    };
    if (!this['~standard'].async)
      try {
        const i = this._parseSync({ data: t, path: [], parent: n });
        return Is(i) ? { value: i.value } : { issues: n.common.issues };
      } catch (i) {
        ((s = (r = i == null ? void 0 : i.message) == null ? void 0 : r.toLowerCase()) != null &&
          s.includes('encountered') &&
          (this['~standard'].async = !0),
          (n.common = { issues: [], async: !0 }));
      }
    return this._parseAsync({ data: t, path: [], parent: n }).then((i) =>
      Is(i) ? { value: i.value } : { issues: n.common.issues },
    );
  }
  async parseAsync(t, n) {
    const r = await this.safeParseAsync(t, n);
    if (r.success) return r.data;
    throw r.error;
  }
  async safeParseAsync(t, n) {
    const r = {
        common: { issues: [], contextualErrorMap: n == null ? void 0 : n.errorMap, async: !0 },
        path: (n == null ? void 0 : n.path) || [],
        schemaErrorMap: this._def.errorMap,
        parent: null,
        data: t,
        parsedType: Ln(t),
      },
      s = this._parse({ data: t, path: r.path, parent: r }),
      i = await (ma(s) ? s : Promise.resolve(s));
    return Mf(r, i);
  }
  refine(t, n) {
    const r = (s) =>
      typeof n == 'string' || typeof n > 'u' ? { message: n } : typeof n == 'function' ? n(s) : n;
    return this._refinement((s, i) => {
      const l = t(s),
        a = () => i.addIssue({ code: T.custom, ...r(s) });
      return typeof Promise < 'u' && l instanceof Promise
        ? l.then((o) => (o ? !0 : (a(), !1)))
        : l
          ? !0
          : (a(), !1);
    });
  }
  refinement(t, n) {
    return this._refinement((r, s) =>
      t(r) ? !0 : (s.addIssue(typeof n == 'function' ? n(r, s) : n), !1),
    );
  }
  _refinement(t) {
    return new zs({
      schema: this,
      typeName: J.ZodEffects,
      effect: { type: 'refinement', refinement: t },
    });
  }
  superRefine(t) {
    return this._refinement(t);
  }
  constructor(t) {
    ((this.spa = this.safeParseAsync),
      (this._def = t),
      (this.parse = this.parse.bind(this)),
      (this.safeParse = this.safeParse.bind(this)),
      (this.parseAsync = this.parseAsync.bind(this)),
      (this.safeParseAsync = this.safeParseAsync.bind(this)),
      (this.spa = this.spa.bind(this)),
      (this.refine = this.refine.bind(this)),
      (this.refinement = this.refinement.bind(this)),
      (this.superRefine = this.superRefine.bind(this)),
      (this.optional = this.optional.bind(this)),
      (this.nullable = this.nullable.bind(this)),
      (this.nullish = this.nullish.bind(this)),
      (this.array = this.array.bind(this)),
      (this.promise = this.promise.bind(this)),
      (this.or = this.or.bind(this)),
      (this.and = this.and.bind(this)),
      (this.transform = this.transform.bind(this)),
      (this.brand = this.brand.bind(this)),
      (this.default = this.default.bind(this)),
      (this.catch = this.catch.bind(this)),
      (this.describe = this.describe.bind(this)),
      (this.pipe = this.pipe.bind(this)),
      (this.readonly = this.readonly.bind(this)),
      (this.isNullable = this.isNullable.bind(this)),
      (this.isOptional = this.isOptional.bind(this)),
      (this['~standard'] = { version: 1, vendor: 'zod', validate: (n) => this['~validate'](n) }));
  }
  optional() {
    return ar.create(this, this._def);
  }
  nullable() {
    return Us.create(this, this._def);
  }
  nullish() {
    return this.nullable().optional();
  }
  array() {
    return ln.create(this);
  }
  promise() {
    return xa.create(this, this._def);
  }
  or(t) {
    return va.create([this, t], this._def);
  }
  and(t) {
    return ga.create(this, t, this._def);
  }
  transform(t) {
    return new zs({
      ...re(this._def),
      schema: this,
      typeName: J.ZodEffects,
      effect: { type: 'transform', transform: t },
    });
  }
  default(t) {
    const n = typeof t == 'function' ? t : () => t;
    return new Fu({ ...re(this._def), innerType: this, defaultValue: n, typeName: J.ZodDefault });
  }
  brand() {
    return new qw({ typeName: J.ZodBranded, type: this, ...re(this._def) });
  }
  catch(t) {
    const n = typeof t == 'function' ? t : () => t;
    return new Iu({ ...re(this._def), innerType: this, catchValue: n, typeName: J.ZodCatch });
  }
  describe(t) {
    const n = this.constructor;
    return new n({ ...this._def, description: t });
  }
  pipe(t) {
    return Bc.create(this, t);
  }
  readonly() {
    return Mu.create(this);
  }
  isOptional() {
    return this.safeParse(void 0).success;
  }
  isNullable() {
    return this.safeParse(null).success;
  }
}
const jw = /^c[^\s-]{8,}$/i,
  Rw = /^[0-9a-z]+$/,
  Tw = /^[0-9A-HJKMNP-TV-Z]{26}$/i,
  Ow = /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/i,
  Pw = /^[a-z0-9_-]{21}$/i,
  bw = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/,
  Aw =
    /^[-+]?P(?!$)(?:(?:[-+]?\d+Y)|(?:[-+]?\d+[.,]\d+Y$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:(?:[-+]?\d+W)|(?:[-+]?\d+[.,]\d+W$))?(?:(?:[-+]?\d+D)|(?:[-+]?\d+[.,]\d+D$))?(?:T(?=[\d+-])(?:(?:[-+]?\d+H)|(?:[-+]?\d+[.,]\d+H$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:[-+]?\d+(?:[.,]\d+)?S)?)??$/,
  Lw = /^(?!\.)(?!.*\.\.)([A-Z0-9_'+\-\.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$/i,
  Fw = '^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$';
let xo;
const Iw =
    /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$/,
  Mw =
    /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\/(3[0-2]|[12]?[0-9])$/,
  Dw =
    /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/,
  zw =
    /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(12[0-8]|1[01][0-9]|[1-9]?[0-9])$/,
  Uw = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/,
  Vw = /^([0-9a-zA-Z-_]{4})*(([0-9a-zA-Z-_]{2}(==)?)|([0-9a-zA-Z-_]{3}(=)?))?$/,
  ay =
    '((\\d\\d[2468][048]|\\d\\d[13579][26]|\\d\\d0[48]|[02468][048]00|[13579][26]00)-02-29|\\d{4}-((0[13578]|1[02])-(0[1-9]|[12]\\d|3[01])|(0[469]|11)-(0[1-9]|[12]\\d|30)|(02)-(0[1-9]|1\\d|2[0-8])))',
  $w = new RegExp(`^${ay}$`);
function oy(e) {
  let t = '[0-5]\\d';
  e.precision ? (t = `${t}\\.\\d{${e.precision}}`) : e.precision == null && (t = `${t}(\\.\\d+)?`);
  const n = e.precision ? '+' : '?';
  return `([01]\\d|2[0-3]):[0-5]\\d(:${t})${n}`;
}
function Bw(e) {
  return new RegExp(`^${oy(e)}$`);
}
function Qw(e) {
  let t = `${ay}T${oy(e)}`;
  const n = [];
  return (
    n.push(e.local ? 'Z?' : 'Z'),
    e.offset && n.push('([+-]\\d{2}:?\\d{2})'),
    (t = `${t}(${n.join('|')})`),
    new RegExp(`^${t}$`)
  );
}
function Ww(e, t) {
  return !!(((t === 'v4' || !t) && Iw.test(e)) || ((t === 'v6' || !t) && Dw.test(e)));
}
function Zw(e, t) {
  if (!bw.test(e)) return !1;
  try {
    const [n] = e.split('.');
    if (!n) return !1;
    const r = n
        .replace(/-/g, '+')
        .replace(/_/g, '/')
        .padEnd(n.length + ((4 - (n.length % 4)) % 4), '='),
      s = JSON.parse(atob(r));
    return !(
      typeof s != 'object' ||
      s === null ||
      ('typ' in s && (s == null ? void 0 : s.typ) !== 'JWT') ||
      !s.alg ||
      (t && s.alg !== t)
    );
  } catch {
    return !1;
  }
}
function Hw(e, t) {
  return !!(((t === 'v4' || !t) && Mw.test(e)) || ((t === 'v6' || !t) && zw.test(e)));
}
class Gn extends ue {
  _parse(t) {
    if ((this._def.coerce && (t.data = String(t.data)), this._getType(t) !== B.string)) {
      const i = this._getOrReturnCtx(t);
      return (z(i, { code: T.invalid_type, expected: B.string, received: i.parsedType }), X);
    }
    const r = new kt();
    let s;
    for (const i of this._def.checks)
      if (i.kind === 'min')
        t.data.length < i.value &&
          ((s = this._getOrReturnCtx(t, s)),
          z(s, {
            code: T.too_small,
            minimum: i.value,
            type: 'string',
            inclusive: !0,
            exact: !1,
            message: i.message,
          }),
          r.dirty());
      else if (i.kind === 'max')
        t.data.length > i.value &&
          ((s = this._getOrReturnCtx(t, s)),
          z(s, {
            code: T.too_big,
            maximum: i.value,
            type: 'string',
            inclusive: !0,
            exact: !1,
            message: i.message,
          }),
          r.dirty());
      else if (i.kind === 'length') {
        const l = t.data.length > i.value,
          a = t.data.length < i.value;
        (l || a) &&
          ((s = this._getOrReturnCtx(t, s)),
          l
            ? z(s, {
                code: T.too_big,
                maximum: i.value,
                type: 'string',
                inclusive: !0,
                exact: !0,
                message: i.message,
              })
            : a &&
              z(s, {
                code: T.too_small,
                minimum: i.value,
                type: 'string',
                inclusive: !0,
                exact: !0,
                message: i.message,
              }),
          r.dirty());
      } else if (i.kind === 'email')
        Lw.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'email', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'emoji')
        (xo || (xo = new RegExp(Fw, 'u')),
          xo.test(t.data) ||
            ((s = this._getOrReturnCtx(t, s)),
            z(s, { validation: 'emoji', code: T.invalid_string, message: i.message }),
            r.dirty()));
      else if (i.kind === 'uuid')
        Ow.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'uuid', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'nanoid')
        Pw.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'nanoid', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'cuid')
        jw.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'cuid', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'cuid2')
        Rw.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'cuid2', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'ulid')
        Tw.test(t.data) ||
          ((s = this._getOrReturnCtx(t, s)),
          z(s, { validation: 'ulid', code: T.invalid_string, message: i.message }),
          r.dirty());
      else if (i.kind === 'url')
        try {
          new URL(t.data);
        } catch {
          ((s = this._getOrReturnCtx(t, s)),
            z(s, { validation: 'url', code: T.invalid_string, message: i.message }),
            r.dirty());
        }
      else
        i.kind === 'regex'
          ? ((i.regex.lastIndex = 0),
            i.regex.test(t.data) ||
              ((s = this._getOrReturnCtx(t, s)),
              z(s, { validation: 'regex', code: T.invalid_string, message: i.message }),
              r.dirty()))
          : i.kind === 'trim'
            ? (t.data = t.data.trim())
            : i.kind === 'includes'
              ? t.data.includes(i.value, i.position) ||
                ((s = this._getOrReturnCtx(t, s)),
                z(s, {
                  code: T.invalid_string,
                  validation: { includes: i.value, position: i.position },
                  message: i.message,
                }),
                r.dirty())
              : i.kind === 'toLowerCase'
                ? (t.data = t.data.toLowerCase())
                : i.kind === 'toUpperCase'
                  ? (t.data = t.data.toUpperCase())
                  : i.kind === 'startsWith'
                    ? t.data.startsWith(i.value) ||
                      ((s = this._getOrReturnCtx(t, s)),
                      z(s, {
                        code: T.invalid_string,
                        validation: { startsWith: i.value },
                        message: i.message,
                      }),
                      r.dirty())
                    : i.kind === 'endsWith'
                      ? t.data.endsWith(i.value) ||
                        ((s = this._getOrReturnCtx(t, s)),
                        z(s, {
                          code: T.invalid_string,
                          validation: { endsWith: i.value },
                          message: i.message,
                        }),
                        r.dirty())
                      : i.kind === 'datetime'
                        ? Qw(i).test(t.data) ||
                          ((s = this._getOrReturnCtx(t, s)),
                          z(s, {
                            code: T.invalid_string,
                            validation: 'datetime',
                            message: i.message,
                          }),
                          r.dirty())
                        : i.kind === 'date'
                          ? $w.test(t.data) ||
                            ((s = this._getOrReturnCtx(t, s)),
                            z(s, {
                              code: T.invalid_string,
                              validation: 'date',
                              message: i.message,
                            }),
                            r.dirty())
                          : i.kind === 'time'
                            ? Bw(i).test(t.data) ||
                              ((s = this._getOrReturnCtx(t, s)),
                              z(s, {
                                code: T.invalid_string,
                                validation: 'time',
                                message: i.message,
                              }),
                              r.dirty())
                            : i.kind === 'duration'
                              ? Aw.test(t.data) ||
                                ((s = this._getOrReturnCtx(t, s)),
                                z(s, {
                                  validation: 'duration',
                                  code: T.invalid_string,
                                  message: i.message,
                                }),
                                r.dirty())
                              : i.kind === 'ip'
                                ? Ww(t.data, i.version) ||
                                  ((s = this._getOrReturnCtx(t, s)),
                                  z(s, {
                                    validation: 'ip',
                                    code: T.invalid_string,
                                    message: i.message,
                                  }),
                                  r.dirty())
                                : i.kind === 'jwt'
                                  ? Zw(t.data, i.alg) ||
                                    ((s = this._getOrReturnCtx(t, s)),
                                    z(s, {
                                      validation: 'jwt',
                                      code: T.invalid_string,
                                      message: i.message,
                                    }),
                                    r.dirty())
                                  : i.kind === 'cidr'
                                    ? Hw(t.data, i.version) ||
                                      ((s = this._getOrReturnCtx(t, s)),
                                      z(s, {
                                        validation: 'cidr',
                                        code: T.invalid_string,
                                        message: i.message,
                                      }),
                                      r.dirty())
                                    : i.kind === 'base64'
                                      ? Uw.test(t.data) ||
                                        ((s = this._getOrReturnCtx(t, s)),
                                        z(s, {
                                          validation: 'base64',
                                          code: T.invalid_string,
                                          message: i.message,
                                        }),
                                        r.dirty())
                                      : i.kind === 'base64url'
                                        ? Vw.test(t.data) ||
                                          ((s = this._getOrReturnCtx(t, s)),
                                          z(s, {
                                            validation: 'base64url',
                                            code: T.invalid_string,
                                            message: i.message,
                                          }),
                                          r.dirty())
                                        : ce.assertNever(i);
    return { status: r.value, value: t.data };
  }
  _regex(t, n, r) {
    return this.refinement((s) => t.test(s), {
      validation: n,
      code: T.invalid_string,
      ...Q.errToObj(r),
    });
  }
  _addCheck(t) {
    return new Gn({ ...this._def, checks: [...this._def.checks, t] });
  }
  email(t) {
    return this._addCheck({ kind: 'email', ...Q.errToObj(t) });
  }
  url(t) {
    return this._addCheck({ kind: 'url', ...Q.errToObj(t) });
  }
  emoji(t) {
    return this._addCheck({ kind: 'emoji', ...Q.errToObj(t) });
  }
  uuid(t) {
    return this._addCheck({ kind: 'uuid', ...Q.errToObj(t) });
  }
  nanoid(t) {
    return this._addCheck({ kind: 'nanoid', ...Q.errToObj(t) });
  }
  cuid(t) {
    return this._addCheck({ kind: 'cuid', ...Q.errToObj(t) });
  }
  cuid2(t) {
    return this._addCheck({ kind: 'cuid2', ...Q.errToObj(t) });
  }
  ulid(t) {
    return this._addCheck({ kind: 'ulid', ...Q.errToObj(t) });
  }
  base64(t) {
    return this._addCheck({ kind: 'base64', ...Q.errToObj(t) });
  }
  base64url(t) {
    return this._addCheck({ kind: 'base64url', ...Q.errToObj(t) });
  }
  jwt(t) {
    return this._addCheck({ kind: 'jwt', ...Q.errToObj(t) });
  }
  ip(t) {
    return this._addCheck({ kind: 'ip', ...Q.errToObj(t) });
  }
  cidr(t) {
    return this._addCheck({ kind: 'cidr', ...Q.errToObj(t) });
  }
  datetime(t) {
    return typeof t == 'string'
      ? this._addCheck({ kind: 'datetime', precision: null, offset: !1, local: !1, message: t })
      : this._addCheck({
          kind: 'datetime',
          precision:
            typeof (t == null ? void 0 : t.precision) > 'u'
              ? null
              : t == null
                ? void 0
                : t.precision,
          offset: (t == null ? void 0 : t.offset) ?? !1,
          local: (t == null ? void 0 : t.local) ?? !1,
          ...Q.errToObj(t == null ? void 0 : t.message),
        });
  }
  date(t) {
    return this._addCheck({ kind: 'date', message: t });
  }
  time(t) {
    return typeof t == 'string'
      ? this._addCheck({ kind: 'time', precision: null, message: t })
      : this._addCheck({
          kind: 'time',
          precision:
            typeof (t == null ? void 0 : t.precision) > 'u'
              ? null
              : t == null
                ? void 0
                : t.precision,
          ...Q.errToObj(t == null ? void 0 : t.message),
        });
  }
  duration(t) {
    return this._addCheck({ kind: 'duration', ...Q.errToObj(t) });
  }
  regex(t, n) {
    return this._addCheck({ kind: 'regex', regex: t, ...Q.errToObj(n) });
  }
  includes(t, n) {
    return this._addCheck({
      kind: 'includes',
      value: t,
      position: n == null ? void 0 : n.position,
      ...Q.errToObj(n == null ? void 0 : n.message),
    });
  }
  startsWith(t, n) {
    return this._addCheck({ kind: 'startsWith', value: t, ...Q.errToObj(n) });
  }
  endsWith(t, n) {
    return this._addCheck({ kind: 'endsWith', value: t, ...Q.errToObj(n) });
  }
  min(t, n) {
    return this._addCheck({ kind: 'min', value: t, ...Q.errToObj(n) });
  }
  max(t, n) {
    return this._addCheck({ kind: 'max', value: t, ...Q.errToObj(n) });
  }
  length(t, n) {
    return this._addCheck({ kind: 'length', value: t, ...Q.errToObj(n) });
  }
  nonempty(t) {
    return this.min(1, Q.errToObj(t));
  }
  trim() {
    return new Gn({ ...this._def, checks: [...this._def.checks, { kind: 'trim' }] });
  }
  toLowerCase() {
    return new Gn({ ...this._def, checks: [...this._def.checks, { kind: 'toLowerCase' }] });
  }
  toUpperCase() {
    return new Gn({ ...this._def, checks: [...this._def.checks, { kind: 'toUpperCase' }] });
  }
  get isDatetime() {
    return !!this._def.checks.find((t) => t.kind === 'datetime');
  }
  get isDate() {
    return !!this._def.checks.find((t) => t.kind === 'date');
  }
  get isTime() {
    return !!this._def.checks.find((t) => t.kind === 'time');
  }
  get isDuration() {
    return !!this._def.checks.find((t) => t.kind === 'duration');
  }
  get isEmail() {
    return !!this._def.checks.find((t) => t.kind === 'email');
  }
  get isURL() {
    return !!this._def.checks.find((t) => t.kind === 'url');
  }
  get isEmoji() {
    return !!this._def.checks.find((t) => t.kind === 'emoji');
  }
  get isUUID() {
    return !!this._def.checks.find((t) => t.kind === 'uuid');
  }
  get isNANOID() {
    return !!this._def.checks.find((t) => t.kind === 'nanoid');
  }
  get isCUID() {
    return !!this._def.checks.find((t) => t.kind === 'cuid');
  }
  get isCUID2() {
    return !!this._def.checks.find((t) => t.kind === 'cuid2');
  }
  get isULID() {
    return !!this._def.checks.find((t) => t.kind === 'ulid');
  }
  get isIP() {
    return !!this._def.checks.find((t) => t.kind === 'ip');
  }
  get isCIDR() {
    return !!this._def.checks.find((t) => t.kind === 'cidr');
  }
  get isBase64() {
    return !!this._def.checks.find((t) => t.kind === 'base64');
  }
  get isBase64url() {
    return !!this._def.checks.find((t) => t.kind === 'base64url');
  }
  get minLength() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'min' && (t === null || n.value > t) && (t = n.value);
    return t;
  }
  get maxLength() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'max' && (t === null || n.value < t) && (t = n.value);
    return t;
  }
}
Gn.create = (e) =>
  new Gn({
    checks: [],
    typeName: J.ZodString,
    coerce: (e == null ? void 0 : e.coerce) ?? !1,
    ...re(e),
  });
function Kw(e, t) {
  const n = (e.toString().split('.')[1] || '').length,
    r = (t.toString().split('.')[1] || '').length,
    s = n > r ? n : r,
    i = Number.parseInt(e.toFixed(s).replace('.', '')),
    l = Number.parseInt(t.toFixed(s).replace('.', ''));
  return (i % l) / 10 ** s;
}
class Ms extends ue {
  constructor() {
    (super(...arguments),
      (this.min = this.gte),
      (this.max = this.lte),
      (this.step = this.multipleOf));
  }
  _parse(t) {
    if ((this._def.coerce && (t.data = Number(t.data)), this._getType(t) !== B.number)) {
      const i = this._getOrReturnCtx(t);
      return (z(i, { code: T.invalid_type, expected: B.number, received: i.parsedType }), X);
    }
    let r;
    const s = new kt();
    for (const i of this._def.checks)
      i.kind === 'int'
        ? ce.isInteger(t.data) ||
          ((r = this._getOrReturnCtx(t, r)),
          z(r, {
            code: T.invalid_type,
            expected: 'integer',
            received: 'float',
            message: i.message,
          }),
          s.dirty())
        : i.kind === 'min'
          ? (i.inclusive ? t.data < i.value : t.data <= i.value) &&
            ((r = this._getOrReturnCtx(t, r)),
            z(r, {
              code: T.too_small,
              minimum: i.value,
              type: 'number',
              inclusive: i.inclusive,
              exact: !1,
              message: i.message,
            }),
            s.dirty())
          : i.kind === 'max'
            ? (i.inclusive ? t.data > i.value : t.data >= i.value) &&
              ((r = this._getOrReturnCtx(t, r)),
              z(r, {
                code: T.too_big,
                maximum: i.value,
                type: 'number',
                inclusive: i.inclusive,
                exact: !1,
                message: i.message,
              }),
              s.dirty())
            : i.kind === 'multipleOf'
              ? Kw(t.data, i.value) !== 0 &&
                ((r = this._getOrReturnCtx(t, r)),
                z(r, { code: T.not_multiple_of, multipleOf: i.value, message: i.message }),
                s.dirty())
              : i.kind === 'finite'
                ? Number.isFinite(t.data) ||
                  ((r = this._getOrReturnCtx(t, r)),
                  z(r, { code: T.not_finite, message: i.message }),
                  s.dirty())
                : ce.assertNever(i);
    return { status: s.value, value: t.data };
  }
  gte(t, n) {
    return this.setLimit('min', t, !0, Q.toString(n));
  }
  gt(t, n) {
    return this.setLimit('min', t, !1, Q.toString(n));
  }
  lte(t, n) {
    return this.setLimit('max', t, !0, Q.toString(n));
  }
  lt(t, n) {
    return this.setLimit('max', t, !1, Q.toString(n));
  }
  setLimit(t, n, r, s) {
    return new Ms({
      ...this._def,
      checks: [...this._def.checks, { kind: t, value: n, inclusive: r, message: Q.toString(s) }],
    });
  }
  _addCheck(t) {
    return new Ms({ ...this._def, checks: [...this._def.checks, t] });
  }
  int(t) {
    return this._addCheck({ kind: 'int', message: Q.toString(t) });
  }
  positive(t) {
    return this._addCheck({ kind: 'min', value: 0, inclusive: !1, message: Q.toString(t) });
  }
  negative(t) {
    return this._addCheck({ kind: 'max', value: 0, inclusive: !1, message: Q.toString(t) });
  }
  nonpositive(t) {
    return this._addCheck({ kind: 'max', value: 0, inclusive: !0, message: Q.toString(t) });
  }
  nonnegative(t) {
    return this._addCheck({ kind: 'min', value: 0, inclusive: !0, message: Q.toString(t) });
  }
  multipleOf(t, n) {
    return this._addCheck({ kind: 'multipleOf', value: t, message: Q.toString(n) });
  }
  finite(t) {
    return this._addCheck({ kind: 'finite', message: Q.toString(t) });
  }
  safe(t) {
    return this._addCheck({
      kind: 'min',
      inclusive: !0,
      value: Number.MIN_SAFE_INTEGER,
      message: Q.toString(t),
    })._addCheck({
      kind: 'max',
      inclusive: !0,
      value: Number.MAX_SAFE_INTEGER,
      message: Q.toString(t),
    });
  }
  get minValue() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'min' && (t === null || n.value > t) && (t = n.value);
    return t;
  }
  get maxValue() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'max' && (t === null || n.value < t) && (t = n.value);
    return t;
  }
  get isInt() {
    return !!this._def.checks.find(
      (t) => t.kind === 'int' || (t.kind === 'multipleOf' && ce.isInteger(t.value)),
    );
  }
  get isFinite() {
    let t = null,
      n = null;
    for (const r of this._def.checks) {
      if (r.kind === 'finite' || r.kind === 'int' || r.kind === 'multipleOf') return !0;
      r.kind === 'min'
        ? (n === null || r.value > n) && (n = r.value)
        : r.kind === 'max' && (t === null || r.value < t) && (t = r.value);
    }
    return Number.isFinite(n) && Number.isFinite(t);
  }
}
Ms.create = (e) =>
  new Ms({
    checks: [],
    typeName: J.ZodNumber,
    coerce: (e == null ? void 0 : e.coerce) || !1,
    ...re(e),
  });
class $i extends ue {
  constructor() {
    (super(...arguments), (this.min = this.gte), (this.max = this.lte));
  }
  _parse(t) {
    if (this._def.coerce)
      try {
        t.data = BigInt(t.data);
      } catch {
        return this._getInvalidInput(t);
      }
    if (this._getType(t) !== B.bigint) return this._getInvalidInput(t);
    let r;
    const s = new kt();
    for (const i of this._def.checks)
      i.kind === 'min'
        ? (i.inclusive ? t.data < i.value : t.data <= i.value) &&
          ((r = this._getOrReturnCtx(t, r)),
          z(r, {
            code: T.too_small,
            type: 'bigint',
            minimum: i.value,
            inclusive: i.inclusive,
            message: i.message,
          }),
          s.dirty())
        : i.kind === 'max'
          ? (i.inclusive ? t.data > i.value : t.data >= i.value) &&
            ((r = this._getOrReturnCtx(t, r)),
            z(r, {
              code: T.too_big,
              type: 'bigint',
              maximum: i.value,
              inclusive: i.inclusive,
              message: i.message,
            }),
            s.dirty())
          : i.kind === 'multipleOf'
            ? t.data % i.value !== BigInt(0) &&
              ((r = this._getOrReturnCtx(t, r)),
              z(r, { code: T.not_multiple_of, multipleOf: i.value, message: i.message }),
              s.dirty())
            : ce.assertNever(i);
    return { status: s.value, value: t.data };
  }
  _getInvalidInput(t) {
    const n = this._getOrReturnCtx(t);
    return (z(n, { code: T.invalid_type, expected: B.bigint, received: n.parsedType }), X);
  }
  gte(t, n) {
    return this.setLimit('min', t, !0, Q.toString(n));
  }
  gt(t, n) {
    return this.setLimit('min', t, !1, Q.toString(n));
  }
  lte(t, n) {
    return this.setLimit('max', t, !0, Q.toString(n));
  }
  lt(t, n) {
    return this.setLimit('max', t, !1, Q.toString(n));
  }
  setLimit(t, n, r, s) {
    return new $i({
      ...this._def,
      checks: [...this._def.checks, { kind: t, value: n, inclusive: r, message: Q.toString(s) }],
    });
  }
  _addCheck(t) {
    return new $i({ ...this._def, checks: [...this._def.checks, t] });
  }
  positive(t) {
    return this._addCheck({ kind: 'min', value: BigInt(0), inclusive: !1, message: Q.toString(t) });
  }
  negative(t) {
    return this._addCheck({ kind: 'max', value: BigInt(0), inclusive: !1, message: Q.toString(t) });
  }
  nonpositive(t) {
    return this._addCheck({ kind: 'max', value: BigInt(0), inclusive: !0, message: Q.toString(t) });
  }
  nonnegative(t) {
    return this._addCheck({ kind: 'min', value: BigInt(0), inclusive: !0, message: Q.toString(t) });
  }
  multipleOf(t, n) {
    return this._addCheck({ kind: 'multipleOf', value: t, message: Q.toString(n) });
  }
  get minValue() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'min' && (t === null || n.value > t) && (t = n.value);
    return t;
  }
  get maxValue() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'max' && (t === null || n.value < t) && (t = n.value);
    return t;
  }
}
$i.create = (e) =>
  new $i({
    checks: [],
    typeName: J.ZodBigInt,
    coerce: (e == null ? void 0 : e.coerce) ?? !1,
    ...re(e),
  });
class Df extends ue {
  _parse(t) {
    if ((this._def.coerce && (t.data = !!t.data), this._getType(t) !== B.boolean)) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.boolean, received: r.parsedType }), X);
    }
    return Ft(t.data);
  }
}
Df.create = (e) =>
  new Df({ typeName: J.ZodBoolean, coerce: (e == null ? void 0 : e.coerce) || !1, ...re(e) });
class ya extends ue {
  _parse(t) {
    if ((this._def.coerce && (t.data = new Date(t.data)), this._getType(t) !== B.date)) {
      const i = this._getOrReturnCtx(t);
      return (z(i, { code: T.invalid_type, expected: B.date, received: i.parsedType }), X);
    }
    if (Number.isNaN(t.data.getTime())) {
      const i = this._getOrReturnCtx(t);
      return (z(i, { code: T.invalid_date }), X);
    }
    const r = new kt();
    let s;
    for (const i of this._def.checks)
      i.kind === 'min'
        ? t.data.getTime() < i.value &&
          ((s = this._getOrReturnCtx(t, s)),
          z(s, {
            code: T.too_small,
            message: i.message,
            inclusive: !0,
            exact: !1,
            minimum: i.value,
            type: 'date',
          }),
          r.dirty())
        : i.kind === 'max'
          ? t.data.getTime() > i.value &&
            ((s = this._getOrReturnCtx(t, s)),
            z(s, {
              code: T.too_big,
              message: i.message,
              inclusive: !0,
              exact: !1,
              maximum: i.value,
              type: 'date',
            }),
            r.dirty())
          : ce.assertNever(i);
    return { status: r.value, value: new Date(t.data.getTime()) };
  }
  _addCheck(t) {
    return new ya({ ...this._def, checks: [...this._def.checks, t] });
  }
  min(t, n) {
    return this._addCheck({ kind: 'min', value: t.getTime(), message: Q.toString(n) });
  }
  max(t, n) {
    return this._addCheck({ kind: 'max', value: t.getTime(), message: Q.toString(n) });
  }
  get minDate() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'min' && (t === null || n.value > t) && (t = n.value);
    return t != null ? new Date(t) : null;
  }
  get maxDate() {
    let t = null;
    for (const n of this._def.checks)
      n.kind === 'max' && (t === null || n.value < t) && (t = n.value);
    return t != null ? new Date(t) : null;
  }
}
ya.create = (e) =>
  new ya({
    checks: [],
    coerce: (e == null ? void 0 : e.coerce) || !1,
    typeName: J.ZodDate,
    ...re(e),
  });
class zf extends ue {
  _parse(t) {
    if (this._getType(t) !== B.symbol) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.symbol, received: r.parsedType }), X);
    }
    return Ft(t.data);
  }
}
zf.create = (e) => new zf({ typeName: J.ZodSymbol, ...re(e) });
class Uf extends ue {
  _parse(t) {
    if (this._getType(t) !== B.undefined) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.undefined, received: r.parsedType }), X);
    }
    return Ft(t.data);
  }
}
Uf.create = (e) => new Uf({ typeName: J.ZodUndefined, ...re(e) });
class Vf extends ue {
  _parse(t) {
    if (this._getType(t) !== B.null) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.null, received: r.parsedType }), X);
    }
    return Ft(t.data);
  }
}
Vf.create = (e) => new Vf({ typeName: J.ZodNull, ...re(e) });
class $f extends ue {
  constructor() {
    (super(...arguments), (this._any = !0));
  }
  _parse(t) {
    return Ft(t.data);
  }
}
$f.create = (e) => new $f({ typeName: J.ZodAny, ...re(e) });
class Bf extends ue {
  constructor() {
    (super(...arguments), (this._unknown = !0));
  }
  _parse(t) {
    return Ft(t.data);
  }
}
Bf.create = (e) => new Bf({ typeName: J.ZodUnknown, ...re(e) });
class dr extends ue {
  _parse(t) {
    const n = this._getOrReturnCtx(t);
    return (z(n, { code: T.invalid_type, expected: B.never, received: n.parsedType }), X);
  }
}
dr.create = (e) => new dr({ typeName: J.ZodNever, ...re(e) });
class Qf extends ue {
  _parse(t) {
    if (this._getType(t) !== B.undefined) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.void, received: r.parsedType }), X);
    }
    return Ft(t.data);
  }
}
Qf.create = (e) => new Qf({ typeName: J.ZodVoid, ...re(e) });
class ln extends ue {
  _parse(t) {
    const { ctx: n, status: r } = this._processInputParams(t),
      s = this._def;
    if (n.parsedType !== B.array)
      return (z(n, { code: T.invalid_type, expected: B.array, received: n.parsedType }), X);
    if (s.exactLength !== null) {
      const l = n.data.length > s.exactLength.value,
        a = n.data.length < s.exactLength.value;
      (l || a) &&
        (z(n, {
          code: l ? T.too_big : T.too_small,
          minimum: a ? s.exactLength.value : void 0,
          maximum: l ? s.exactLength.value : void 0,
          type: 'array',
          inclusive: !0,
          exact: !0,
          message: s.exactLength.message,
        }),
        r.dirty());
    }
    if (
      (s.minLength !== null &&
        n.data.length < s.minLength.value &&
        (z(n, {
          code: T.too_small,
          minimum: s.minLength.value,
          type: 'array',
          inclusive: !0,
          exact: !1,
          message: s.minLength.message,
        }),
        r.dirty()),
      s.maxLength !== null &&
        n.data.length > s.maxLength.value &&
        (z(n, {
          code: T.too_big,
          maximum: s.maxLength.value,
          type: 'array',
          inclusive: !0,
          exact: !1,
          message: s.maxLength.message,
        }),
        r.dirty()),
      n.common.async)
    )
      return Promise.all(
        [...n.data].map((l, a) => s.type._parseAsync(new cr(n, l, n.path, a))),
      ).then((l) => kt.mergeArray(r, l));
    const i = [...n.data].map((l, a) => s.type._parseSync(new cr(n, l, n.path, a)));
    return kt.mergeArray(r, i);
  }
  get element() {
    return this._def.type;
  }
  min(t, n) {
    return new ln({ ...this._def, minLength: { value: t, message: Q.toString(n) } });
  }
  max(t, n) {
    return new ln({ ...this._def, maxLength: { value: t, message: Q.toString(n) } });
  }
  length(t, n) {
    return new ln({ ...this._def, exactLength: { value: t, message: Q.toString(n) } });
  }
  nonempty(t) {
    return this.min(1, t);
  }
}
ln.create = (e, t) =>
  new ln({
    type: e,
    minLength: null,
    maxLength: null,
    exactLength: null,
    typeName: J.ZodArray,
    ...re(t),
  });
function Yr(e) {
  if (e instanceof Le) {
    const t = {};
    for (const n in e.shape) {
      const r = e.shape[n];
      t[n] = ar.create(Yr(r));
    }
    return new Le({ ...e._def, shape: () => t });
  } else
    return e instanceof ln
      ? new ln({ ...e._def, type: Yr(e.element) })
      : e instanceof ar
        ? ar.create(Yr(e.unwrap()))
        : e instanceof Us
          ? Us.create(Yr(e.unwrap()))
          : e instanceof $r
            ? $r.create(e.items.map((t) => Yr(t)))
            : e;
}
class Le extends ue {
  constructor() {
    (super(...arguments),
      (this._cached = null),
      (this.nonstrict = this.passthrough),
      (this.augment = this.extend));
  }
  _getCached() {
    if (this._cached !== null) return this._cached;
    const t = this._def.shape(),
      n = ce.objectKeys(t);
    return ((this._cached = { shape: t, keys: n }), this._cached);
  }
  _parse(t) {
    if (this._getType(t) !== B.object) {
      const u = this._getOrReturnCtx(t);
      return (z(u, { code: T.invalid_type, expected: B.object, received: u.parsedType }), X);
    }
    const { status: r, ctx: s } = this._processInputParams(t),
      { shape: i, keys: l } = this._getCached(),
      a = [];
    if (!(this._def.catchall instanceof dr && this._def.unknownKeys === 'strip'))
      for (const u in s.data) l.includes(u) || a.push(u);
    const o = [];
    for (const u of l) {
      const f = i[u],
        h = s.data[u];
      o.push({
        key: { status: 'valid', value: u },
        value: f._parse(new cr(s, h, s.path, u)),
        alwaysSet: u in s.data,
      });
    }
    if (this._def.catchall instanceof dr) {
      const u = this._def.unknownKeys;
      if (u === 'passthrough')
        for (const f of a)
          o.push({
            key: { status: 'valid', value: f },
            value: { status: 'valid', value: s.data[f] },
          });
      else if (u === 'strict')
        a.length > 0 && (z(s, { code: T.unrecognized_keys, keys: a }), r.dirty());
      else if (u !== 'strip')
        throw new Error('Internal ZodObject error: invalid unknownKeys value.');
    } else {
      const u = this._def.catchall;
      for (const f of a) {
        const h = s.data[f];
        o.push({
          key: { status: 'valid', value: f },
          value: u._parse(new cr(s, h, s.path, f)),
          alwaysSet: f in s.data,
        });
      }
    }
    return s.common.async
      ? Promise.resolve()
          .then(async () => {
            const u = [];
            for (const f of o) {
              const h = await f.key,
                p = await f.value;
              u.push({ key: h, value: p, alwaysSet: f.alwaysSet });
            }
            return u;
          })
          .then((u) => kt.mergeObjectSync(r, u))
      : kt.mergeObjectSync(r, o);
  }
  get shape() {
    return this._def.shape();
  }
  strict(t) {
    return (
      Q.errToObj,
      new Le({
        ...this._def,
        unknownKeys: 'strict',
        ...(t !== void 0
          ? {
              errorMap: (n, r) => {
                var i, l;
                const s =
                  ((l = (i = this._def).errorMap) == null ? void 0 : l.call(i, n, r).message) ??
                  r.defaultError;
                return n.code === 'unrecognized_keys'
                  ? { message: Q.errToObj(t).message ?? s }
                  : { message: s };
              },
            }
          : {}),
      })
    );
  }
  strip() {
    return new Le({ ...this._def, unknownKeys: 'strip' });
  }
  passthrough() {
    return new Le({ ...this._def, unknownKeys: 'passthrough' });
  }
  extend(t) {
    return new Le({ ...this._def, shape: () => ({ ...this._def.shape(), ...t }) });
  }
  merge(t) {
    return new Le({
      unknownKeys: t._def.unknownKeys,
      catchall: t._def.catchall,
      shape: () => ({ ...this._def.shape(), ...t._def.shape() }),
      typeName: J.ZodObject,
    });
  }
  setKey(t, n) {
    return this.augment({ [t]: n });
  }
  catchall(t) {
    return new Le({ ...this._def, catchall: t });
  }
  pick(t) {
    const n = {};
    for (const r of ce.objectKeys(t)) t[r] && this.shape[r] && (n[r] = this.shape[r]);
    return new Le({ ...this._def, shape: () => n });
  }
  omit(t) {
    const n = {};
    for (const r of ce.objectKeys(this.shape)) t[r] || (n[r] = this.shape[r]);
    return new Le({ ...this._def, shape: () => n });
  }
  deepPartial() {
    return Yr(this);
  }
  partial(t) {
    const n = {};
    for (const r of ce.objectKeys(this.shape)) {
      const s = this.shape[r];
      t && !t[r] ? (n[r] = s) : (n[r] = s.optional());
    }
    return new Le({ ...this._def, shape: () => n });
  }
  required(t) {
    const n = {};
    for (const r of ce.objectKeys(this.shape))
      if (t && !t[r]) n[r] = this.shape[r];
      else {
        let i = this.shape[r];
        for (; i instanceof ar; ) i = i._def.innerType;
        n[r] = i;
      }
    return new Le({ ...this._def, shape: () => n });
  }
  keyof() {
    return uy(ce.objectKeys(this.shape));
  }
}
Le.create = (e, t) =>
  new Le({
    shape: () => e,
    unknownKeys: 'strip',
    catchall: dr.create(),
    typeName: J.ZodObject,
    ...re(t),
  });
Le.strictCreate = (e, t) =>
  new Le({
    shape: () => e,
    unknownKeys: 'strict',
    catchall: dr.create(),
    typeName: J.ZodObject,
    ...re(t),
  });
Le.lazycreate = (e, t) =>
  new Le({
    shape: e,
    unknownKeys: 'strip',
    catchall: dr.create(),
    typeName: J.ZodObject,
    ...re(t),
  });
class va extends ue {
  _parse(t) {
    const { ctx: n } = this._processInputParams(t),
      r = this._def.options;
    function s(i) {
      for (const a of i) if (a.result.status === 'valid') return a.result;
      for (const a of i)
        if (a.result.status === 'dirty')
          return (n.common.issues.push(...a.ctx.common.issues), a.result);
      const l = i.map((a) => new En(a.ctx.common.issues));
      return (z(n, { code: T.invalid_union, unionErrors: l }), X);
    }
    if (n.common.async)
      return Promise.all(
        r.map(async (i) => {
          const l = { ...n, common: { ...n.common, issues: [] }, parent: null };
          return { result: await i._parseAsync({ data: n.data, path: n.path, parent: l }), ctx: l };
        }),
      ).then(s);
    {
      let i;
      const l = [];
      for (const o of r) {
        const u = { ...n, common: { ...n.common, issues: [] }, parent: null },
          f = o._parseSync({ data: n.data, path: n.path, parent: u });
        if (f.status === 'valid') return f;
        (f.status === 'dirty' && !i && (i = { result: f, ctx: u }),
          u.common.issues.length && l.push(u.common.issues));
      }
      if (i) return (n.common.issues.push(...i.ctx.common.issues), i.result);
      const a = l.map((o) => new En(o));
      return (z(n, { code: T.invalid_union, unionErrors: a }), X);
    }
  }
  get options() {
    return this._def.options;
  }
}
va.create = (e, t) => new va({ options: e, typeName: J.ZodUnion, ...re(t) });
function Lu(e, t) {
  const n = Ln(e),
    r = Ln(t);
  if (e === t) return { valid: !0, data: e };
  if (n === B.object && r === B.object) {
    const s = ce.objectKeys(t),
      i = ce.objectKeys(e).filter((a) => s.indexOf(a) !== -1),
      l = { ...e, ...t };
    for (const a of i) {
      const o = Lu(e[a], t[a]);
      if (!o.valid) return { valid: !1 };
      l[a] = o.data;
    }
    return { valid: !0, data: l };
  } else if (n === B.array && r === B.array) {
    if (e.length !== t.length) return { valid: !1 };
    const s = [];
    for (let i = 0; i < e.length; i++) {
      const l = e[i],
        a = t[i],
        o = Lu(l, a);
      if (!o.valid) return { valid: !1 };
      s.push(o.data);
    }
    return { valid: !0, data: s };
  } else return n === B.date && r === B.date && +e == +t ? { valid: !0, data: e } : { valid: !1 };
}
class ga extends ue {
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t),
      s = (i, l) => {
        if (Ff(i) || Ff(l)) return X;
        const a = Lu(i.value, l.value);
        return a.valid
          ? ((If(i) || If(l)) && n.dirty(), { status: n.value, value: a.data })
          : (z(r, { code: T.invalid_intersection_types }), X);
      };
    return r.common.async
      ? Promise.all([
          this._def.left._parseAsync({ data: r.data, path: r.path, parent: r }),
          this._def.right._parseAsync({ data: r.data, path: r.path, parent: r }),
        ]).then(([i, l]) => s(i, l))
      : s(
          this._def.left._parseSync({ data: r.data, path: r.path, parent: r }),
          this._def.right._parseSync({ data: r.data, path: r.path, parent: r }),
        );
  }
}
ga.create = (e, t, n) => new ga({ left: e, right: t, typeName: J.ZodIntersection, ...re(n) });
class $r extends ue {
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t);
    if (r.parsedType !== B.array)
      return (z(r, { code: T.invalid_type, expected: B.array, received: r.parsedType }), X);
    if (r.data.length < this._def.items.length)
      return (
        z(r, {
          code: T.too_small,
          minimum: this._def.items.length,
          inclusive: !0,
          exact: !1,
          type: 'array',
        }),
        X
      );
    !this._def.rest &&
      r.data.length > this._def.items.length &&
      (z(r, {
        code: T.too_big,
        maximum: this._def.items.length,
        inclusive: !0,
        exact: !1,
        type: 'array',
      }),
      n.dirty());
    const i = [...r.data]
      .map((l, a) => {
        const o = this._def.items[a] || this._def.rest;
        return o ? o._parse(new cr(r, l, r.path, a)) : null;
      })
      .filter((l) => !!l);
    return r.common.async ? Promise.all(i).then((l) => kt.mergeArray(n, l)) : kt.mergeArray(n, i);
  }
  get items() {
    return this._def.items;
  }
  rest(t) {
    return new $r({ ...this._def, rest: t });
  }
}
$r.create = (e, t) => {
  if (!Array.isArray(e)) throw new Error('You must pass an array of schemas to z.tuple([ ... ])');
  return new $r({ items: e, typeName: J.ZodTuple, rest: null, ...re(t) });
};
class Wf extends ue {
  get keySchema() {
    return this._def.keyType;
  }
  get valueSchema() {
    return this._def.valueType;
  }
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t);
    if (r.parsedType !== B.map)
      return (z(r, { code: T.invalid_type, expected: B.map, received: r.parsedType }), X);
    const s = this._def.keyType,
      i = this._def.valueType,
      l = [...r.data.entries()].map(([a, o], u) => ({
        key: s._parse(new cr(r, a, r.path, [u, 'key'])),
        value: i._parse(new cr(r, o, r.path, [u, 'value'])),
      }));
    if (r.common.async) {
      const a = new Map();
      return Promise.resolve().then(async () => {
        for (const o of l) {
          const u = await o.key,
            f = await o.value;
          if (u.status === 'aborted' || f.status === 'aborted') return X;
          ((u.status === 'dirty' || f.status === 'dirty') && n.dirty(), a.set(u.value, f.value));
        }
        return { status: n.value, value: a };
      });
    } else {
      const a = new Map();
      for (const o of l) {
        const u = o.key,
          f = o.value;
        if (u.status === 'aborted' || f.status === 'aborted') return X;
        ((u.status === 'dirty' || f.status === 'dirty') && n.dirty(), a.set(u.value, f.value));
      }
      return { status: n.value, value: a };
    }
  }
}
Wf.create = (e, t, n) => new Wf({ valueType: t, keyType: e, typeName: J.ZodMap, ...re(n) });
class Bi extends ue {
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t);
    if (r.parsedType !== B.set)
      return (z(r, { code: T.invalid_type, expected: B.set, received: r.parsedType }), X);
    const s = this._def;
    (s.minSize !== null &&
      r.data.size < s.minSize.value &&
      (z(r, {
        code: T.too_small,
        minimum: s.minSize.value,
        type: 'set',
        inclusive: !0,
        exact: !1,
        message: s.minSize.message,
      }),
      n.dirty()),
      s.maxSize !== null &&
        r.data.size > s.maxSize.value &&
        (z(r, {
          code: T.too_big,
          maximum: s.maxSize.value,
          type: 'set',
          inclusive: !0,
          exact: !1,
          message: s.maxSize.message,
        }),
        n.dirty()));
    const i = this._def.valueType;
    function l(o) {
      const u = new Set();
      for (const f of o) {
        if (f.status === 'aborted') return X;
        (f.status === 'dirty' && n.dirty(), u.add(f.value));
      }
      return { status: n.value, value: u };
    }
    const a = [...r.data.values()].map((o, u) => i._parse(new cr(r, o, r.path, u)));
    return r.common.async ? Promise.all(a).then((o) => l(o)) : l(a);
  }
  min(t, n) {
    return new Bi({ ...this._def, minSize: { value: t, message: Q.toString(n) } });
  }
  max(t, n) {
    return new Bi({ ...this._def, maxSize: { value: t, message: Q.toString(n) } });
  }
  size(t, n) {
    return this.min(t, n).max(t, n);
  }
  nonempty(t) {
    return this.min(1, t);
  }
}
Bi.create = (e, t) =>
  new Bi({ valueType: e, minSize: null, maxSize: null, typeName: J.ZodSet, ...re(t) });
class Zf extends ue {
  get schema() {
    return this._def.getter();
  }
  _parse(t) {
    const { ctx: n } = this._processInputParams(t);
    return this._def.getter()._parse({ data: n.data, path: n.path, parent: n });
  }
}
Zf.create = (e, t) => new Zf({ getter: e, typeName: J.ZodLazy, ...re(t) });
class Hf extends ue {
  _parse(t) {
    if (t.data !== this._def.value) {
      const n = this._getOrReturnCtx(t);
      return (z(n, { received: n.data, code: T.invalid_literal, expected: this._def.value }), X);
    }
    return { status: 'valid', value: t.data };
  }
  get value() {
    return this._def.value;
  }
}
Hf.create = (e, t) => new Hf({ value: e, typeName: J.ZodLiteral, ...re(t) });
function uy(e, t) {
  return new Ds({ values: e, typeName: J.ZodEnum, ...re(t) });
}
class Ds extends ue {
  _parse(t) {
    if (typeof t.data != 'string') {
      const n = this._getOrReturnCtx(t),
        r = this._def.values;
      return (
        z(n, { expected: ce.joinValues(r), received: n.parsedType, code: T.invalid_type }),
        X
      );
    }
    if ((this._cache || (this._cache = new Set(this._def.values)), !this._cache.has(t.data))) {
      const n = this._getOrReturnCtx(t),
        r = this._def.values;
      return (z(n, { received: n.data, code: T.invalid_enum_value, options: r }), X);
    }
    return Ft(t.data);
  }
  get options() {
    return this._def.values;
  }
  get enum() {
    const t = {};
    for (const n of this._def.values) t[n] = n;
    return t;
  }
  get Values() {
    const t = {};
    for (const n of this._def.values) t[n] = n;
    return t;
  }
  get Enum() {
    const t = {};
    for (const n of this._def.values) t[n] = n;
    return t;
  }
  extract(t, n = this._def) {
    return Ds.create(t, { ...this._def, ...n });
  }
  exclude(t, n = this._def) {
    return Ds.create(
      this.options.filter((r) => !t.includes(r)),
      { ...this._def, ...n },
    );
  }
}
Ds.create = uy;
class Kf extends ue {
  _parse(t) {
    const n = ce.getValidEnumValues(this._def.values),
      r = this._getOrReturnCtx(t);
    if (r.parsedType !== B.string && r.parsedType !== B.number) {
      const s = ce.objectValues(n);
      return (
        z(r, { expected: ce.joinValues(s), received: r.parsedType, code: T.invalid_type }),
        X
      );
    }
    if (
      (this._cache || (this._cache = new Set(ce.getValidEnumValues(this._def.values))),
      !this._cache.has(t.data))
    ) {
      const s = ce.objectValues(n);
      return (z(r, { received: r.data, code: T.invalid_enum_value, options: s }), X);
    }
    return Ft(t.data);
  }
  get enum() {
    return this._def.values;
  }
}
Kf.create = (e, t) => new Kf({ values: e, typeName: J.ZodNativeEnum, ...re(t) });
class xa extends ue {
  unwrap() {
    return this._def.type;
  }
  _parse(t) {
    const { ctx: n } = this._processInputParams(t);
    if (n.parsedType !== B.promise && n.common.async === !1)
      return (z(n, { code: T.invalid_type, expected: B.promise, received: n.parsedType }), X);
    const r = n.parsedType === B.promise ? n.data : Promise.resolve(n.data);
    return Ft(
      r.then((s) =>
        this._def.type.parseAsync(s, { path: n.path, errorMap: n.common.contextualErrorMap }),
      ),
    );
  }
}
xa.create = (e, t) => new xa({ type: e, typeName: J.ZodPromise, ...re(t) });
class zs extends ue {
  innerType() {
    return this._def.schema;
  }
  sourceType() {
    return this._def.schema._def.typeName === J.ZodEffects
      ? this._def.schema.sourceType()
      : this._def.schema;
  }
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t),
      s = this._def.effect || null,
      i = {
        addIssue: (l) => {
          (z(r, l), l.fatal ? n.abort() : n.dirty());
        },
        get path() {
          return r.path;
        },
      };
    if (((i.addIssue = i.addIssue.bind(i)), s.type === 'preprocess')) {
      const l = s.transform(r.data, i);
      if (r.common.async)
        return Promise.resolve(l).then(async (a) => {
          if (n.value === 'aborted') return X;
          const o = await this._def.schema._parseAsync({ data: a, path: r.path, parent: r });
          return o.status === 'aborted'
            ? X
            : o.status === 'dirty' || n.value === 'dirty'
              ? ci(o.value)
              : o;
        });
      {
        if (n.value === 'aborted') return X;
        const a = this._def.schema._parseSync({ data: l, path: r.path, parent: r });
        return a.status === 'aborted'
          ? X
          : a.status === 'dirty' || n.value === 'dirty'
            ? ci(a.value)
            : a;
      }
    }
    if (s.type === 'refinement') {
      const l = (a) => {
        const o = s.refinement(a, i);
        if (r.common.async) return Promise.resolve(o);
        if (o instanceof Promise)
          throw new Error(
            'Async refinement encountered during synchronous parse operation. Use .parseAsync instead.',
          );
        return a;
      };
      if (r.common.async === !1) {
        const a = this._def.schema._parseSync({ data: r.data, path: r.path, parent: r });
        return a.status === 'aborted'
          ? X
          : (a.status === 'dirty' && n.dirty(), l(a.value), { status: n.value, value: a.value });
      } else
        return this._def.schema
          ._parseAsync({ data: r.data, path: r.path, parent: r })
          .then((a) =>
            a.status === 'aborted'
              ? X
              : (a.status === 'dirty' && n.dirty(),
                l(a.value).then(() => ({ status: n.value, value: a.value }))),
          );
    }
    if (s.type === 'transform')
      if (r.common.async === !1) {
        const l = this._def.schema._parseSync({ data: r.data, path: r.path, parent: r });
        if (!Is(l)) return X;
        const a = s.transform(l.value, i);
        if (a instanceof Promise)
          throw new Error(
            'Asynchronous transform encountered during synchronous parse operation. Use .parseAsync instead.',
          );
        return { status: n.value, value: a };
      } else
        return this._def.schema
          ._parseAsync({ data: r.data, path: r.path, parent: r })
          .then((l) =>
            Is(l)
              ? Promise.resolve(s.transform(l.value, i)).then((a) => ({
                  status: n.value,
                  value: a,
                }))
              : X,
          );
    ce.assertNever(s);
  }
}
zs.create = (e, t, n) => new zs({ schema: e, typeName: J.ZodEffects, effect: t, ...re(n) });
zs.createWithPreprocess = (e, t, n) =>
  new zs({
    schema: t,
    effect: { type: 'preprocess', transform: e },
    typeName: J.ZodEffects,
    ...re(n),
  });
class ar extends ue {
  _parse(t) {
    return this._getType(t) === B.undefined ? Ft(void 0) : this._def.innerType._parse(t);
  }
  unwrap() {
    return this._def.innerType;
  }
}
ar.create = (e, t) => new ar({ innerType: e, typeName: J.ZodOptional, ...re(t) });
class Us extends ue {
  _parse(t) {
    return this._getType(t) === B.null ? Ft(null) : this._def.innerType._parse(t);
  }
  unwrap() {
    return this._def.innerType;
  }
}
Us.create = (e, t) => new Us({ innerType: e, typeName: J.ZodNullable, ...re(t) });
class Fu extends ue {
  _parse(t) {
    const { ctx: n } = this._processInputParams(t);
    let r = n.data;
    return (
      n.parsedType === B.undefined && (r = this._def.defaultValue()),
      this._def.innerType._parse({ data: r, path: n.path, parent: n })
    );
  }
  removeDefault() {
    return this._def.innerType;
  }
}
Fu.create = (e, t) =>
  new Fu({
    innerType: e,
    typeName: J.ZodDefault,
    defaultValue: typeof t.default == 'function' ? t.default : () => t.default,
    ...re(t),
  });
class Iu extends ue {
  _parse(t) {
    const { ctx: n } = this._processInputParams(t),
      r = { ...n, common: { ...n.common, issues: [] } },
      s = this._def.innerType._parse({ data: r.data, path: r.path, parent: { ...r } });
    return ma(s)
      ? s.then((i) => ({
          status: 'valid',
          value:
            i.status === 'valid'
              ? i.value
              : this._def.catchValue({
                  get error() {
                    return new En(r.common.issues);
                  },
                  input: r.data,
                }),
        }))
      : {
          status: 'valid',
          value:
            s.status === 'valid'
              ? s.value
              : this._def.catchValue({
                  get error() {
                    return new En(r.common.issues);
                  },
                  input: r.data,
                }),
        };
  }
  removeCatch() {
    return this._def.innerType;
  }
}
Iu.create = (e, t) =>
  new Iu({
    innerType: e,
    typeName: J.ZodCatch,
    catchValue: typeof t.catch == 'function' ? t.catch : () => t.catch,
    ...re(t),
  });
class qf extends ue {
  _parse(t) {
    if (this._getType(t) !== B.nan) {
      const r = this._getOrReturnCtx(t);
      return (z(r, { code: T.invalid_type, expected: B.nan, received: r.parsedType }), X);
    }
    return { status: 'valid', value: t.data };
  }
}
qf.create = (e) => new qf({ typeName: J.ZodNaN, ...re(e) });
class qw extends ue {
  _parse(t) {
    const { ctx: n } = this._processInputParams(t),
      r = n.data;
    return this._def.type._parse({ data: r, path: n.path, parent: n });
  }
  unwrap() {
    return this._def.type;
  }
}
class Bc extends ue {
  _parse(t) {
    const { status: n, ctx: r } = this._processInputParams(t);
    if (r.common.async)
      return (async () => {
        const i = await this._def.in._parseAsync({ data: r.data, path: r.path, parent: r });
        return i.status === 'aborted'
          ? X
          : i.status === 'dirty'
            ? (n.dirty(), ci(i.value))
            : this._def.out._parseAsync({ data: i.value, path: r.path, parent: r });
      })();
    {
      const s = this._def.in._parseSync({ data: r.data, path: r.path, parent: r });
      return s.status === 'aborted'
        ? X
        : s.status === 'dirty'
          ? (n.dirty(), { status: 'dirty', value: s.value })
          : this._def.out._parseSync({ data: s.value, path: r.path, parent: r });
    }
  }
  static create(t, n) {
    return new Bc({ in: t, out: n, typeName: J.ZodPipeline });
  }
}
class Mu extends ue {
  _parse(t) {
    const n = this._def.innerType._parse(t),
      r = (s) => (Is(s) && (s.value = Object.freeze(s.value)), s);
    return ma(n) ? n.then((s) => r(s)) : r(n);
  }
  unwrap() {
    return this._def.innerType;
  }
}
Mu.create = (e, t) => new Mu({ innerType: e, typeName: J.ZodReadonly, ...re(t) });
var J;
(function (e) {
  ((e.ZodString = 'ZodString'),
    (e.ZodNumber = 'ZodNumber'),
    (e.ZodNaN = 'ZodNaN'),
    (e.ZodBigInt = 'ZodBigInt'),
    (e.ZodBoolean = 'ZodBoolean'),
    (e.ZodDate = 'ZodDate'),
    (e.ZodSymbol = 'ZodSymbol'),
    (e.ZodUndefined = 'ZodUndefined'),
    (e.ZodNull = 'ZodNull'),
    (e.ZodAny = 'ZodAny'),
    (e.ZodUnknown = 'ZodUnknown'),
    (e.ZodNever = 'ZodNever'),
    (e.ZodVoid = 'ZodVoid'),
    (e.ZodArray = 'ZodArray'),
    (e.ZodObject = 'ZodObject'),
    (e.ZodUnion = 'ZodUnion'),
    (e.ZodDiscriminatedUnion = 'ZodDiscriminatedUnion'),
    (e.ZodIntersection = 'ZodIntersection'),
    (e.ZodTuple = 'ZodTuple'),
    (e.ZodRecord = 'ZodRecord'),
    (e.ZodMap = 'ZodMap'),
    (e.ZodSet = 'ZodSet'),
    (e.ZodFunction = 'ZodFunction'),
    (e.ZodLazy = 'ZodLazy'),
    (e.ZodLiteral = 'ZodLiteral'),
    (e.ZodEnum = 'ZodEnum'),
    (e.ZodEffects = 'ZodEffects'),
    (e.ZodNativeEnum = 'ZodNativeEnum'),
    (e.ZodOptional = 'ZodOptional'),
    (e.ZodNullable = 'ZodNullable'),
    (e.ZodDefault = 'ZodDefault'),
    (e.ZodCatch = 'ZodCatch'),
    (e.ZodPromise = 'ZodPromise'),
    (e.ZodBranded = 'ZodBranded'),
    (e.ZodPipeline = 'ZodPipeline'),
    (e.ZodReadonly = 'ZodReadonly'));
})(J || (J = {}));
const Gf = Gn.create,
  Yf = Ms.create;
dr.create;
ln.create;
const Gw = Le.create;
va.create;
ga.create;
$r.create;
const Yw = Ds.create;
xa.create;
ar.create;
Us.create;
const Xf = (e, t, n) => {
    if (e && 'reportValidity' in e) {
      const r = $(n, t);
      (e.setCustomValidity((r && r.message) || ''), e.reportValidity());
    }
  },
  cy = (e, t) => {
    for (const n in t.fields) {
      const r = t.fields[n];
      r && r.ref && 'reportValidity' in r.ref
        ? Xf(r.ref, n, e)
        : r.refs && r.refs.forEach((s) => Xf(s, n, e));
    }
  },
  Xw = (e, t) => {
    t.shouldUseNativeValidation && cy(e, t);
    const n = {};
    for (const r in e) {
      const s = $(t.fields, r),
        i = Object.assign(e[r] || {}, { ref: s && s.ref });
      if (Jw(t.names || Object.keys(e), r)) {
        const l = Object.assign({}, $(n, r));
        (ye(l, 'root', i), ye(n, r, l));
      } else ye(n, r, i);
    }
    return n;
  },
  Jw = (e, t) => e.some((n) => n.startsWith(t + '.'));
var e_ = function (e, t) {
    for (var n = {}; e.length; ) {
      var r = e[0],
        s = r.code,
        i = r.message,
        l = r.path.join('.');
      if (!n[l])
        if ('unionErrors' in r) {
          var a = r.unionErrors[0].errors[0];
          n[l] = { message: a.message, type: a.code };
        } else n[l] = { message: i, type: s };
      if (
        ('unionErrors' in r &&
          r.unionErrors.forEach(function (f) {
            return f.errors.forEach(function (h) {
              return e.push(h);
            });
          }),
        t)
      ) {
        var o = n[l].types,
          u = o && o[r.code];
        n[l] = ey(l, t, n, s, u ? [].concat(u, r.message) : r.message);
      }
      e.shift();
    }
    return n;
  },
  t_ = function (e, t, n) {
    return (
      n === void 0 && (n = {}),
      function (r, s, i) {
        try {
          return Promise.resolve(
            (function (l, a) {
              try {
                var o = Promise.resolve(e[n.mode === 'sync' ? 'parse' : 'parseAsync'](r, t)).then(
                  function (u) {
                    return (
                      i.shouldUseNativeValidation && cy({}, i),
                      { errors: {}, values: n.raw ? r : u }
                    );
                  },
                );
              } catch (u) {
                return a(u);
              }
              return o && o.then ? o.then(void 0, a) : o;
            })(0, function (l) {
              if (
                (function (a) {
                  return Array.isArray(a == null ? void 0 : a.errors);
                })(l)
              )
                return {
                  values: {},
                  errors: Xw(
                    e_(l.errors, !i.shouldUseNativeValidation && i.criteriaMode === 'all'),
                    i,
                  ),
                };
              throw l;
            }),
          );
        } catch (l) {
          return Promise.reject(l);
        }
      }
    );
  };
const n_ = 'user_123';
class dy extends Error {
  constructor(n, r, s, i) {
    super(n);
    Hs(this, 'status');
    Hs(this, 'detail');
    Hs(this, 'retryAfter');
    ((this.status = r), (this.detail = s), (this.retryAfter = i));
  }
}
async function yr(e, t = {}, n = !1) {
  const r = { 'content-type': 'application/json' };
  n && (r['X-User-Id'] = n_);
  const s = await fetch(`${Xm}${e}`, { ...t, headers: { ...r, ...(t.headers || {}) } });
  if (!s.ok) {
    const i = s.headers.get('Retry-After') ? parseInt(s.headers.get('Retry-After'), 10) : void 0;
    let l;
    try {
      l = await s.json();
    } catch {}
    throw new dy((l == null ? void 0 : l.error) || s.statusText, s.status, l, i);
  }
  return s.json();
}
const Qc = {
  health: () => yr('/health'),
  deepHealth: () => yr('/healthz/deep'),
  oddsBest: (e) => yr(`/odds/best${e ? `?market=${encodeURIComponent(e)}` : ''}`),
  register: (e) => yr('/me/register', { method: 'POST', body: JSON.stringify(e) }),
  myBets: () => yr('/me/bets', {}, !0),
  createBet: (e) => {
    if (qm)
      throw new dy('Bet creation disabled in beta view-only mode.', 403, { reason: 'view_only' });
    return yr('/me/bets', { method: 'POST', body: JSON.stringify(e) }, !0);
  },
  subscribe: () => yr('/digest/subscribe', { method: 'POST' }, !0),
};
function r_() {
  return R0({ queryKey: ['me', 'bets'], queryFn: Qc.myBets });
}
function s_() {
  const e = Mc();
  return T0({
    mutationFn: Qc.createBet,
    onSuccess: () => {
      e.invalidateQueries({ queryKey: ['me', 'bets'] });
    },
  });
}
const i_ = Gw({
  game_id: Gf().min(3),
  market: Yw(['spread', 'total', 'moneyline']),
  selection: Gf().min(2),
  stake: Yf().min(1),
  odds: Yf().min(1.01),
});
function l_() {
  const e = qm,
    t = Gm,
    n = Ym,
    { data: r } = r_(),
    s = s_(),
    [i, l] = E.useState(null),
    {
      register: a,
      handleSubmit: o,
      reset: u,
      formState: { errors: f },
    } = Sw({
      resolver: t_(i_),
      defaultValues: { market: 'spread', selection: 'HOME', stake: 50, odds: 1.91 },
    }),
    h = (p) => {
      if (e) {
        l({
          message: 'Bet creation is disabled while we are in beta view-only mode.',
          type: 'error',
        });
        return;
      }
      s.mutate(p, {
        onSuccess: () => {
          (l({ message: 'Bet created', type: 'success' }), u());
        },
        onError: (k) => {
          l({ message: (k == null ? void 0 : k.message) || 'Error', type: 'error' });
        },
      });
    };
  return c.jsxs('section', {
    className: 'space-y-6',
    children: [
      c.jsx('h1', { className: 'text-xl font-semibold', children: 'My Bets' }),
      e &&
        c.jsxs('div', {
          className: 'card border-l-4 border-yellow-500 bg-yellow-50 p-4 text-yellow-800',
          role: 'alert',
          children: [
            c.jsx('h2', { className: 'font-semibold text-yellow-900', children: n }),
            c.jsx('p', { className: 'mt-2 text-sm', children: t }),
            c.jsx('p', {
              className: 'mt-2 text-xs text-yellow-700',
              children: 'Bet creation is disabled while we verify data quality.',
            }),
          ],
        }),
      c.jsx('div', {
        className: 'card p-4',
        children: c.jsx('form', {
          onSubmit: o(h),
          children: c.jsxs('fieldset', {
            disabled: e,
            className: 'grid grid-cols-1 md:grid-cols-6 gap-3',
            children: [
              c.jsxs('div', {
                className: 'md:col-span-2',
                children: [
                  c.jsx('label', { className: 'text-sm', children: 'Game ID' }),
                  c.jsx('input', {
                    className: 'input',
                    ...a('game_id'),
                    placeholder: 'NE@DEN-2025-10-05',
                  }),
                  f.game_id &&
                    c.jsx('p', { className: 'text-xs text-red-600', children: f.game_id.message }),
                ],
              }),
              c.jsxs('div', {
                children: [
                  c.jsx('label', { className: 'text-sm', children: 'Market' }),
                  c.jsxs('select', {
                    className: 'select',
                    ...a('market'),
                    defaultValue: 'spread',
                    children: [
                      c.jsx('option', { value: 'spread', children: 'spread' }),
                      c.jsx('option', { value: 'total', children: 'total' }),
                      c.jsx('option', { value: 'moneyline', children: 'moneyline' }),
                    ],
                  }),
                ],
              }),
              c.jsxs('div', {
                children: [
                  c.jsx('label', { className: 'text-sm', children: 'Selection' }),
                  c.jsxs('select', {
                    className: 'select',
                    ...a('selection'),
                    defaultValue: 'HOME',
                    children: [
                      c.jsx('option', { value: 'HOME', children: 'HOME' }),
                      c.jsx('option', { value: 'AWAY', children: 'AWAY' }),
                      c.jsx('option', { value: 'Over', children: 'Over' }),
                      c.jsx('option', { value: 'Under', children: 'Under' }),
                    ],
                  }),
                ],
              }),
              c.jsxs('div', {
                children: [
                  c.jsx('label', { className: 'text-sm', children: 'Stake' }),
                  c.jsx('input', {
                    type: 'number',
                    step: '1',
                    className: 'input',
                    ...a('stake', { valueAsNumber: !0 }),
                  }),
                  f.stake &&
                    c.jsx('p', { className: 'text-xs text-red-600', children: f.stake.message }),
                ],
              }),
              c.jsxs('div', {
                children: [
                  c.jsx('label', { className: 'text-sm', children: 'Odds (decimal)' }),
                  c.jsx('input', {
                    type: 'number',
                    step: '0.01',
                    className: 'input',
                    ...a('odds', { valueAsNumber: !0 }),
                  }),
                  f.odds &&
                    c.jsx('p', { className: 'text-xs text-red-600', children: f.odds.message }),
                ],
              }),
              c.jsx('div', {
                className: 'md:col-span-6 flex items-end justify-end',
                children: c.jsx('button', {
                  className: 'btn',
                  type: 'submit',
                  children: 'Create Bet',
                }),
              }),
            ],
          }),
        }),
      }),
      c.jsxs('div', {
        className: 'card p-4',
        children: [
          c.jsx('h2', { className: 'font-medium mb-3', children: 'Recent Bets' }),
          r != null && r.length
            ? c.jsx('ul', {
                className: 'space-y-2 text-sm',
                children: r.map((p) =>
                  c.jsxs(
                    'li',
                    {
                      className: 'border rounded-lg p-2 flex justify-between',
                      children: [
                        c.jsxs('span', {
                          children: [p.game_id, ' — ', p.market, ' — ', p.selection],
                        }),
                        c.jsxs('span', { children: [p.stake, ' @ ', p.odds] }),
                      ],
                    },
                    p.id,
                  ),
                ),
              })
            : c.jsx('div', { className: 'text-sm text-gray-600', children: 'No bets yet.' }),
        ],
      }),
    ],
  });
}
function a_() {
  const [e, t] = E.useState(!1),
    [n, r] = E.useState(null);
  async function s() {
    t(!0);
    try {
      const i = await Qc.subscribe();
      r({ message: i.message || 'Subscribed', type: 'success' });
    } catch (i) {
      r({ message: (i == null ? void 0 : i.message) || 'Error', type: 'error' });
    } finally {
      t(!1);
    }
  }
  return c.jsxs('section', {
    className: 'space-y-4',
    children: [
      c.jsx('h1', { className: 'text-xl font-semibold', children: 'Weekly Digest' }),
      c.jsxs('div', {
        className: 'card p-4 flex items-center justify-between',
        children: [
          c.jsx('div', {
            className: 'text-sm text-gray-700',
            children: 'Subscribe your account to receive the weekly odds digest.',
          }),
          c.jsx('button', { className: 'btn', onClick: s, disabled: e, children: 'Subscribe' }),
        ],
      }),
      n && c.jsx(Km, { message: n.message, type: n.type, onClose: () => r(null) }),
    ],
  });
}
const fy =
  'This platform provides sports analytics for entertainment purposes only. Not available to residents where prohibited. Users must be 21+. Gamble responsibly.';
function o_() {
  const e = 'user_123';
  return c.jsxs('section', {
    className: 'space-y-4',
    children: [
      c.jsx('h1', { className: 'text-xl font-semibold', children: 'Account' }),
      c.jsxs('div', {
        className: 'card p-4 space-y-2',
        children: [
          c.jsxs('div', {
            className: 'text-sm',
            children: [
              'User ID (from ',
              c.jsx('code', { children: 'VITE_DEMO_USER_ID' }),
              '): ',
              c.jsx('span', { className: 'badge border-gray-300 ml-1', children: e }),
            ],
          }),
          c.jsx('div', { className: 'text-xs text-gray-600', children: fy }),
        ],
      }),
      !e,
    ],
  });
}
function u_({ disclaimer: e }) {
  return c.jsx('footer', {
    className: 'border-t bg-white mt-10',
    children: c.jsx('div', {
      className: 'container py-4 text-xs text-gray-600',
      children: c.jsx('div', { children: e }),
    }),
  });
}
function c_() {
  return c.jsx('header', {
    className: 'border-b bg-white',
    children: c.jsxs('div', {
      className: 'container py-3 flex items-center justify-between',
      children: [
        c.jsxs('div', {
          className: 'flex items-center gap-3',
          children: [
            c.jsx('span', { className: 'text-xl font-semibold', children: 'Bet-That' }),
            c.jsx('span', { className: 'badge border-gray-300', children: 'LOCAL' }),
          ],
        }),
        c.jsxs('nav', {
          className: 'flex gap-3 text-sm',
          children: [
            c.jsx(El, {
              to: '/',
              className: ({ isActive: e }) => (e ? 'underline' : ''),
              children: 'Dashboard',
            }),
            c.jsx(El, {
              to: '/bets',
              className: ({ isActive: e }) => (e ? 'underline' : ''),
              children: 'My Bets',
            }),
            c.jsx(El, {
              to: '/digest',
              className: ({ isActive: e }) => (e ? 'underline' : ''),
              children: 'Digest',
            }),
            c.jsx(El, {
              to: '/account',
              className: ({ isActive: e }) => (e ? 'underline' : ''),
              children: 'Account',
            }),
          ],
        }),
      ],
    }),
  });
}
function d_() {
  return c.jsxs(jx, {
    children: [
      c.jsx(c_, {}),
      c.jsx('main', {
        className: 'container py-6',
        children: c.jsxs(xx, {
          children: [
            c.jsx(ui, { path: '/', element: c.jsx(ew, {}) }),
            c.jsx(ui, { path: '/bets', element: c.jsx(l_, {}) }),
            c.jsx(ui, { path: '/digest', element: c.jsx(a_, {}) }),
            c.jsx(ui, { path: '/account', element: c.jsx(o_, {}) }),
          ],
        }),
      }),
      c.jsx(u_, { disclaimer: fy }),
    ],
  });
}
const f_ = new m0();
wo.createRoot(document.getElementById('root')).render(
  c.jsx(Xe.StrictMode, { children: c.jsx(y0, { client: f_, children: c.jsx(d_, {}) }) }),
);
