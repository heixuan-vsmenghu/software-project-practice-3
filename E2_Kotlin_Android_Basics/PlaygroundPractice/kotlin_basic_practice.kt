data class BoundingBox(
    val left: Int,
    val top: Int,
    val right: Int,
    val bottom: Int
) {
    val area: Int
        get() = (right - left) * (bottom - top)
}

data class RecognitionResult(
    val label: String,
    val confidence: Float,
    val boundingBox: BoundingBox? = null,
    val source: String = "LiteRT"
)

data class UiState(
    val title: String = AppConfig.APP_NAME,
    val imagePath: String? = null,
    val isLoading: Boolean = false,
    val threshold: Float = AppConfig.DEFAULT_THRESHOLD,
    val results: List<RecognitionResult> = emptyList(),
    val message: String = "Waiting for image input"
)

object AppConfig {
    const val APP_NAME = "LiteRT Vision Demo"
    const val MODEL_NAME = "mobilenet_v1_litert.tflite"
    const val DEFAULT_THRESHOLD = 0.60f

    val supportedLabels: Set<String> = setOf("cat", "dog", "person", "bicycle", "cup")
    val labelNames: Map<String, String> = mapOf(
        "cat" to "Cat",
        "dog" to "Dog",
        "person" to "Person",
        "bicycle" to "Bicycle",
        "cup" to "Cup"
    )
}

fun confidenceLevel(confidence: Float): String = when {
    confidence >= 0.90f -> "high"
    confidence >= 0.75f -> "medium"
    confidence >= AppConfig.DEFAULT_THRESHOLD -> "low"
    else -> "ignored"
}

fun displayLabel(label: String): String =
    AppConfig.labelNames[label] ?: "Unknown($label)"

fun formatResult(
    result: RecognitionResult,
    rank: Int = 1,
    showBox: Boolean = true
): String {
    val boxText = result.boundingBox?.let { box ->
        " box=${box.left},${box.top},${box.right},${box.bottom}, area=${box.area}"
    } ?: " box=not provided"

    val confidencePercent = String.format("%.1f", result.confidence * 100)
    val optionalBox = if (showBox) boxText else ""
    return "#$rank ${displayLabel(result.label)} confidence=$confidencePercent% level=${confidenceLevel(result.confidence)}$optionalBox"
}

fun filterRecognitionResults(
    rawResults: List<RecognitionResult>?,
    threshold: Float = AppConfig.DEFAULT_THRESHOLD,
    maxItems: Int = 3,
    onAccepted: (RecognitionResult) -> Unit = {}
): List<RecognitionResult> {
    val safeResults = rawResults ?: emptyList()
    return safeResults
        .filter { it.confidence >= threshold }
        .filter { it.label in AppConfig.supportedLabels }
        .map { it.copy(label = it.label.lowercase()) }
        .sortedByDescending { it.confidence }
        .take(maxItems)
        .also { acceptedResults -> acceptedResults.forEach(onAccepted) }
}

fun buildUiState(
    imagePathFromIntent: String?,
    rawResultsFromModel: List<RecognitionResult>?,
    threshold: Float = AppConfig.DEFAULT_THRESHOLD
): UiState {
    val readablePath = imagePathFromIntent?.let { path ->
        "Image loaded from $path"
    } ?: "No image path from Intent"

    val acceptedResults = filterRecognitionResults(
        rawResults = rawResultsFromModel,
        threshold = threshold,
        maxItems = 4,
        onAccepted = { result ->
            println("Accepted ${result.label} from ${result.source}")
        }
    )

    val message = if (acceptedResults.isEmpty()) {
        "$readablePath, but no result is above threshold $threshold"
    } else {
        "$readablePath, ${acceptedResults.size} result(s) ready for UI"
    }

    return UiState(
        imagePath = imagePathFromIntent,
        threshold = threshold,
        results = acceptedResults,
        message = message
    )
}

fun renderResults(
    results: List<RecognitionResult>,
    renderer: (RecognitionResult) -> String
) {
    results.forEach { result ->
        println(renderer(result))
    }
}

fun printRangeDemos() {
    println("Closed range 1..5:")
    for (i in 1..5) {
        print("$i ")
    }

    println("\nFrame indexes with until:")
    for (index in 0 until 3) {
        print("frame[$index] ")
    }

    println("\nCountdown with downTo and step:")
    for (countdown in 5 downTo 1 step 2) {
        print("$countdown ")
    }
    println()
}

fun main() {
    val appName: String = AppConfig.APP_NAME
    var inferenceCount = 0
    val modelInfo = "${AppConfig.MODEL_NAME} on Android"
    val imagePathFromIntent: String? = "content://gallery/camera_sample.jpg"
    val missingNetworkTitle: String? = null

    println("App: $appName")
    println("Model info: $modelInfo")
    println("Optional title length: ${missingNetworkTitle?.length ?: 0}")
    imagePathFromIntent?.let { println("Intent path length = ${it.length}") }

    val rawResults = listOf(
        RecognitionResult("cat", 0.94f, BoundingBox(24, 36, 220, 260)),
        RecognitionResult("dog", 0.72f, BoundingBox(250, 80, 420, 300)),
        RecognitionResult("car", 0.91f, BoundingBox(10, 10, 140, 120)),
        RecognitionResult("person", 0.88f),
        RecognitionResult("cup", 0.53f, BoundingBox(300, 210, 350, 280))
    )

    val uiState = buildUiState(
        imagePathFromIntent = imagePathFromIntent,
        rawResultsFromModel = rawResults,
        threshold = 0.70f
    )
    inferenceCount += 1

    println("\n${uiState.title} finished inference #$inferenceCount")
    println(uiState.message)

    val labels: Set<String> = uiState.results.map { it.label }.toSet()
    val labelText: List<String> = uiState.results.map { displayLabel(it.label) }
    val groupedByLevel: Map<String, List<RecognitionResult>> = uiState.results.groupBy { confidenceLevel(it.confidence) }

    println("Detected labels set: $labels")
    println("Display labels: $labelText")
    groupedByLevel.forEach { (level, results) ->
        println("Group $level has ${results.size} item(s)")
    }

    println("\nResults rendered by higher-order function:")
    renderResults(uiState.results) { result ->
        formatResult(result = result, rank = uiState.results.indexOf(result) + 1, showBox = true)
    }

    val nextUiState = uiState.copy(
        isLoading = false,
        message = "UI updated with ${uiState.results.size} LiteRT result(s)"
    )
    println("\nCopied UiState message: ${nextUiState.message}")

    printRangeDemos()
}
