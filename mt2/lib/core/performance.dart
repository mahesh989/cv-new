/// Performance optimization utilities for Flutter app
/// Provides caching, lazy loading, widget optimization, and performance monitoring

library performance;

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'architecture.dart';

/// Memory-efficient cache with LRU eviction
class LRUCache<K, V> {
  final int maxSize;
  final Map<K, V> _cache = <K, V>{};
  final List<K> _accessOrder = <K>[];

  LRUCache({this.maxSize = 100});

  V? get(K key) {
    if (_cache.containsKey(key)) {
      // Move to end (most recently used)
      _accessOrder.remove(key);
      _accessOrder.add(key);
      return _cache[key];
    }
    return null;
  }

  void put(K key, V value) {
    if (_cache.containsKey(key)) {
      // Update existing
      _cache[key] = value;
      _accessOrder.remove(key);
      _accessOrder.add(key);
    } else {
      // Add new
      if (_cache.length >= maxSize) {
        // Remove least recently used
        final oldest = _accessOrder.removeAt(0);
        _cache.remove(oldest);
      }
      _cache[key] = value;
      _accessOrder.add(key);
    }
  }

  void remove(K key) {
    _cache.remove(key);
    _accessOrder.remove(key);
  }

  void clear() {
    _cache.clear();
    _accessOrder.clear();
  }

  int get size => _cache.length;
  bool get isEmpty => _cache.isEmpty;
  bool get isNotEmpty => _cache.isNotEmpty;

  Map<String, dynamic> get stats => {
    'size': size,
    'maxSize': maxSize,
    'hitRate': _hitCount / (_hitCount + _missCount),
  };

  int _hitCount = 0;
  int _missCount = 0;
}

/// Enhanced cache manager with persistence and expiration
class CacheManager {
  static final CacheManager _instance = CacheManager._internal();
  factory CacheManager() => _instance;
  CacheManager._internal();

  final LRUCache<String, _CacheEntry> _memoryCache = LRUCache(maxSize: 200);
  late SharedPreferences _prefs;
  bool _isInitialized = false;

  /// Initialize cache manager
  Future<void> initialize() async {
    if (_isInitialized) return;
    _prefs = await SharedPreferences.getInstance();
    await _loadFromDisk();
    _isInitialized = true;
    Logger.info('📦 Cache manager initialized');
  }

  /// Get cached value
  Future<T?> get<T>(String key) async {
    await _ensureInitialized();
    
    final entry = _memoryCache.get(key);
    if (entry != null) {
      if (entry.isExpired) {
        _memoryCache.remove(key);
        await _removeFromDisk(key);
        return null;
      }
      return entry.value as T?;
    }

    // Try loading from disk
    final diskValue = await _getFromDisk<T>(key);
    if (diskValue != null) {
      _memoryCache.put(key, _CacheEntry(diskValue, entry?.expiresAt));
    }
    
    return diskValue;
  }

  /// Set cached value with optional expiration
  Future<void> set<T>(String key, T value, {Duration? expiration}) async {
    await _ensureInitialized();
    
    final expiresAt = expiration != null 
        ? DateTime.now().add(expiration)
        : null;
    
    final entry = _CacheEntry(value, expiresAt);
    _memoryCache.put(key, entry);
    await _saveToDisk(key, entry);
  }

  /// Remove cached value
  Future<void> remove(String key) async {
    await _ensureInitialized();
    _memoryCache.remove(key);
    await _removeFromDisk(key);
  }

  /// Clear all cached values
  Future<void> clear() async {
    await _ensureInitialized();
    _memoryCache.clear();
    
    final keys = _prefs.getKeys().where((k) => k.startsWith('cache_'));
    for (final key in keys) {
      await _prefs.remove(key);
    }
  }

  /// Get cache statistics
  Map<String, dynamic> get stats => {
    'memoryCache': _memoryCache.stats,
    'isInitialized': _isInitialized,
  };

  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await initialize();
    }
  }

  Future<void> _loadFromDisk() async {
    // Load critical cache entries from disk to memory
    final keys = _prefs.getKeys().where((k) => k.startsWith('cache_'));
    for (final key in keys.take(50)) { // Load only first 50 to avoid memory issues
      final cacheKey = key.substring(6); // Remove 'cache_' prefix
      final entry = await _getFromDisk(cacheKey);
      if (entry != null) {
        _memoryCache.put(cacheKey, _CacheEntry(entry));
      }
    }
  }

  Future<T?> _getFromDisk<T>(String key) async {
    final data = _prefs.getString('cache_$key');
    if (data == null) return null;

    try {
      final json = jsonDecode(data);
      final entry = _CacheEntry.fromJson(json);
      
      if (entry.isExpired) {
        await _removeFromDisk(key);
        return null;
      }
      
      return entry.value as T?;
    } catch (e) {
      Logger.warning('Failed to deserialize cache entry: $key', e);
      await _removeFromDisk(key);
      return null;
    }
  }

  Future<void> _saveToDisk(String key, _CacheEntry entry) async {
    try {
      final data = jsonEncode(entry.toJson());
      await _prefs.setString('cache_$key', data);
    } catch (e) {
      Logger.warning('Failed to save cache entry: $key', e);
    }
  }

  Future<void> _removeFromDisk(String key) async {
    await _prefs.remove('cache_$key');
  }
}

/// Cache entry with expiration support
class _CacheEntry {
  final dynamic value;
  final DateTime? expiresAt;
  final DateTime createdAt;

  _CacheEntry(this.value, [this.expiresAt]) : createdAt = DateTime.now();

  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }

  Map<String, dynamic> toJson() => {
    'value': value,
    'expiresAt': expiresAt?.millisecondsSinceEpoch,
    'createdAt': createdAt.millisecondsSinceEpoch,
  };

  static _CacheEntry fromJson(Map<String, dynamic> json) {
    final expiresAt = json['expiresAt'] != null
        ? DateTime.fromMillisecondsSinceEpoch(json['expiresAt'])
        : null;
    
    return _CacheEntry(json['value'], expiresAt);
  }
}

/// Image cache for optimized image loading
class ImageCacheManager {
  static final ImageCacheManager _instance = ImageCacheManager._internal();
  factory ImageCacheManager() => _instance;
  ImageCacheManager._internal();

  final LRUCache<String, Uint8List> _imageCache = LRUCache(maxSize: 50);

  /// Get cached image data
  Uint8List? getImage(String key) {
    return _imageCache.get(key);
  }

  /// Cache image data
  void cacheImage(String key, Uint8List data) {
    _imageCache.put(key, data);
  }

  /// Clear image cache
  void clear() {
    _imageCache.clear();
  }

  /// Get cache size
  int get cacheSize => _imageCache.size;
}

/// Optimized list widget with lazy loading and caching
class OptimizedListView<T> extends StatefulWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final Future<List<T>> Function()? onLoadMore;
  final Widget? loadingWidget;
  final Widget? emptyWidget;
  final ScrollController? controller;
  final bool shrinkWrap;
  final EdgeInsets? padding;

  const OptimizedListView({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.onLoadMore,
    this.loadingWidget,
    this.emptyWidget,
    this.controller,
    this.shrinkWrap = false,
    this.padding,
  });

  @override
  State<OptimizedListView<T>> createState() => _OptimizedListViewState<T>();
}

class _OptimizedListViewState<T> extends State<OptimizedListView<T>> {
  late ScrollController _scrollController;
  bool _isLoadingMore = false;
  List<T> _items = [];

  @override
  void initState() {
    super.initState();
    _scrollController = widget.controller ?? ScrollController();
    _items = List.from(widget.items);
    
    if (widget.onLoadMore != null) {
      _scrollController.addListener(_onScroll);
    }
  }

  @override
  void didUpdateWidget(OptimizedListView<T> oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.items != widget.items) {
      _items = List.from(widget.items);
    }
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _scrollController.dispose();
    }
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
            _scrollController.position.maxScrollExtent * 0.8 &&
        !_isLoadingMore) {
      _loadMore();
    }
  }

  Future<void> _loadMore() async {
    if (widget.onLoadMore == null || _isLoadingMore) return;

    setState(() {
      _isLoadingMore = true;
    });

    try {
      final moreItems = await widget.onLoadMore!();
      setState(() {
        _items.addAll(moreItems);
        _isLoadingMore = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingMore = false;
      });
      Logger.error('Failed to load more items', e);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_items.isEmpty && widget.emptyWidget != null) {
      return widget.emptyWidget!;
    }

    return ListView.builder(
      controller: _scrollController,
      shrinkWrap: widget.shrinkWrap,
      padding: widget.padding,
      itemCount: _items.length + (_isLoadingMore ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _items.length) {
          // Loading more indicator
          return widget.loadingWidget ??
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: CircularProgressIndicator(),
                ),
              );
        }

        return widget.itemBuilder(context, _items[index], index);
      },
    );
  }
}

/// Optimized image widget with caching and loading states
class OptimizedImage extends StatefulWidget {
  final String imageUrl;
  final String? placeholder;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Widget? errorWidget;
  final Duration cacheDuration;

  const OptimizedImage({
    super.key,
    required this.imageUrl,
    this.placeholder,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.errorWidget,
    this.cacheDuration = const Duration(hours: 24),
  });

  @override
  State<OptimizedImage> createState() => _OptimizedImageState();
}

class _OptimizedImageState extends State<OptimizedImage> {
  Uint8List? _imageData;
  bool _isLoading = true;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  Future<void> _loadImage() async {
    final cache = ImageCacheManager();
    final cached = cache.getImage(widget.imageUrl);
    
    if (cached != null) {
      setState(() {
        _imageData = cached;
        _isLoading = false;
      });
      return;
    }

    try {
      // Simulate image loading (replace with actual HTTP request)
      await Future.delayed(const Duration(milliseconds: 500));
      
      // For demo purposes, create dummy image data
      final dummyData = Uint8List.fromList([0xFF, 0xD8, 0xFF, 0xE0]); // JPEG header
      
      cache.cacheImage(widget.imageUrl, dummyData);
      
      setState(() {
        _imageData = dummyData;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _hasError = true;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Container(
        width: widget.width,
        height: widget.height,
        color: Colors.grey[300],
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_hasError) {
      return widget.errorWidget ??
          Container(
            width: widget.width,
            height: widget.height,
            color: Colors.grey[300],
            child: const Icon(Icons.error),
          );
    }

    return Image.memory(
      _imageData!,
      fit: widget.fit,
      width: widget.width,
      height: widget.height,
    );
  }
}

/// Widget visibility detector for lazy loading
class VisibilityDetector extends StatefulWidget {
  final Widget child;
  final Function(bool isVisible)? onVisibilityChanged;
  final double visibilityThreshold;

  const VisibilityDetector({
    super.key,
    required this.child,
    this.onVisibilityChanged,
    this.visibilityThreshold = 0.1,
  });

  @override
  State<VisibilityDetector> createState() => _VisibilityDetectorState();
}

class _VisibilityDetectorState extends State<VisibilityDetector> {
  bool _isVisible = false;

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        _checkVisibility();
        return false;
      },
      child: widget.child,
    );
  }

  void _checkVisibility() {
    // Simplified visibility check
    // In a real implementation, you'd calculate the actual visibility percentage
    final newVisibility = mounted;
    
    if (newVisibility != _isVisible) {
      _isVisible = newVisibility;
      widget.onVisibilityChanged?.call(_isVisible);
    }
  }
}

/// Performance monitoring widget
class PerformanceMonitorWidget extends StatefulWidget {
  final Widget child;
  final String? operationName;

  const PerformanceMonitorWidget({
    super.key,
    required this.child,
    this.operationName,
  });

  @override
  State<PerformanceMonitorWidget> createState() => _PerformanceMonitorWidgetState();
}

class _PerformanceMonitorWidgetState extends State<PerformanceMonitorWidget> {
  late DateTime _buildStartTime;

  @override
  void initState() {
    super.initState();
    _buildStartTime = DateTime.now();
  }

  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final buildTime = DateTime.now().difference(_buildStartTime);
      if (buildTime.inMilliseconds > 16) { // More than one frame
        Logger.warning(
          'Slow widget build detected: ${widget.operationName ?? 'Unknown'} '
          'took ${buildTime.inMilliseconds}ms',
        );
      }
    });

    return widget.child;
  }
}

/// Memory usage tracker
class MemoryTracker {
  static final MemoryTracker _instance = MemoryTracker._internal();
  factory MemoryTracker() => _instance;
  MemoryTracker._internal();

  Timer? _timer;
  final List<double> _memoryUsage = [];
  final StreamController<double> _memoryController = StreamController.broadcast();

  Stream<double> get memoryStream => _memoryController.stream;

  void startTracking() {
    _timer = Timer.periodic(const Duration(seconds: 5), (_) {
      _checkMemoryUsage();
    });
  }

  void stopTracking() {
    _timer?.cancel();
    _timer = null;
  }

  void _checkMemoryUsage() {
    // Simplified memory tracking
    // In a real implementation, you'd use platform channels to get actual memory usage
    final fakeMemory = DateTime.now().millisecondsSinceEpoch % 100;
    _memoryUsage.add(fakeMemory.toDouble());
    
    if (_memoryUsage.length > 100) {
      _memoryUsage.removeAt(0);
    }
    
    _memoryController.add(fakeMemory.toDouble());
    
    if (fakeMemory > 80) {
      Logger.warning('High memory usage detected: ${fakeMemory}MB');
    }
  }

  double get averageMemoryUsage {
    if (_memoryUsage.isEmpty) return 0;
    return _memoryUsage.reduce((a, b) => a + b) / _memoryUsage.length;
  }

  void dispose() {
    _timer?.cancel();
    _memoryController.close();
  }
}

/// Widget pool for reusing expensive widgets
class WidgetPool<T extends Widget> {
  final List<T> _pool = [];
  final T Function() _creator;
  final int maxSize;

  WidgetPool({
    required T Function() creator,
    this.maxSize = 10,
  }) : _creator = creator;

  T acquire() {
    if (_pool.isNotEmpty) {
      return _pool.removeLast();
    }
    return _creator();
  }

  void release(T widget) {
    if (_pool.length < maxSize) {
      _pool.add(widget);
    }
  }

  void clear() {
    _pool.clear();
  }

  int get poolSize => _pool.length;
}

/// Debouncer for reducing excessive function calls
class Debouncer {
  final Duration delay;
  Timer? _timer;

  Debouncer({required this.delay});

  void run(VoidCallback action) {
    _timer?.cancel();
    _timer = Timer(delay, action);
  }

  void dispose() {
    _timer?.cancel();
  }
}

/// Throttler for limiting function call frequency
class Throttler {
  final Duration duration;
  DateTime? _lastCall;

  Throttler({required this.duration});

  bool run(VoidCallback action) {
    final now = DateTime.now();
    if (_lastCall == null || now.difference(_lastCall!) >= duration) {
      _lastCall = now;
      action();
      return true;
    }
    return false;
  }
}

/// Performance optimization utilities
class PerformanceUtils {
  /// Batch multiple operations to reduce layout thrashing
  static void batchOperations(List<VoidCallback> operations) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      for (final operation in operations) {
        operation();
      }
    });
  }

  /// Optimize list performance by precomputing item heights
  static Map<int, double> precomputeItemHeights<T>(
    List<T> items,
    double Function(T item) heightCalculator,
  ) {
    final heights = <int, double>{};
    for (int i = 0; i < items.length; i++) {
      heights[i] = heightCalculator(items[i]);
    }
    return heights;
  }

  /// Create optimized scroll physics
  static ScrollPhysics createOptimizedScrollPhysics() {
    return const BouncingScrollPhysics(
      parent: AlwaysScrollableScrollPhysics(),
    );
  }
}

/// Global performance manager
final cacheManager = CacheManager();
final imageCache = ImageCacheManager();
final memoryTracker = MemoryTracker();

/// Initialize performance optimizations
Future<void> initializePerformanceOptimizations() async {
  await cacheManager.initialize();
  memoryTracker.startTracking();
  
  // Increase image cache size
  PaintingBinding.instance.imageCache.maximumSize = 200;
  PaintingBinding.instance.imageCache.maximumSizeBytes = 50 * 1024 * 1024; // 50MB
  
  Logger.info('⚡ Performance optimizations initialized');
}
