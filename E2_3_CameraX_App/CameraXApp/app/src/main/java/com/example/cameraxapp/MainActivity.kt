package com.example.cameraxapp

import android.Manifest
import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.MediaStoreOutputOptions
import androidx.camera.video.Quality
import androidx.camera.video.QualitySelector
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.core.content.ContextCompat
import com.example.cameraxapp.databinding.ActivityMainBinding
import java.nio.ByteBuffer
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : ComponentActivity() {

    private lateinit var viewBinding: ActivityMainBinding

    private var imageCapture: ImageCapture? = null
    private var videoCapture: VideoCapture<Recorder>? = null
    private var recording: Recording? = null

    private lateinit var cameraExecutor: ExecutorService

    private var cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
    private var imageAnalysis: ImageAnalysis? = null
    private var isAnalysisEnabled = true
    private var isBackCamera = true

    private val requestPermissionsLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            if (allPermissionsGranted()) {
                updateStatus("Permissions granted")
                startCamera()
            } else {
                updateStatus("Missing camera or audio permission")
                Toast.makeText(
                    this,
                    "Camera and audio permissions are required.",
                    Toast.LENGTH_LONG,
                ).show()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewBinding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(viewBinding.root)

        cameraExecutor = Executors.newSingleThreadExecutor()

        viewBinding.imageCaptureButton.setOnClickListener { takePhoto() }
        viewBinding.videoCaptureButton.setOnClickListener { captureVideo() }
        viewBinding.analysisToggleButton.setOnClickListener { toggleAnalysis() }
        viewBinding.switchCameraButton.setOnClickListener { switchCamera() }

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            updateStatus("Requesting camera permissions")
            requestPermissionsLauncher.launch(requiredPermissions())
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
                }

            val imageCaptureUseCase = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()
            imageCapture = imageCaptureUseCase

            val recorder = Recorder.Builder()
                .setQualitySelector(QualitySelector.from(Quality.HIGHEST))
                .build()
            val videoCaptureUseCase = VideoCapture.withOutput(recorder)
            videoCapture = videoCaptureUseCase

            val analyzer = if (isAnalysisEnabled) {
                ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()
                    .also {
                        it.setAnalyzer(cameraExecutor, LuminosityAnalyzer { luma ->
                            Log.d(TAG, "Average luminosity: ${"%.2f".format(Locale.US, luma)}")
                            runOnUiThread {
                                viewBinding.lumaText.text =
                                    "Average luminosity: ${"%.2f".format(Locale.US, luma)}"
                            }
                        })
                    }
            } else {
                null
            }

            try {
                cameraProvider.unbindAll()

                if (analyzer != null) {
                    cameraProvider.bindToLifecycle(
                        this,
                        cameraSelector,
                        preview,
                        imageCaptureUseCase,
                        videoCaptureUseCase,
                        analyzer,
                    )
                    imageAnalysis = analyzer
                    updateUseCases(includeAnalysis = true)
                    updateStatus("Camera ready")
                } else {
                    cameraProvider.bindToLifecycle(
                        this,
                        cameraSelector,
                        preview,
                        imageCaptureUseCase,
                        videoCaptureUseCase,
                    )
                    imageAnalysis = null
                    viewBinding.lumaText.text = "Average luminosity: --"
                    updateUseCases(includeAnalysis = false)
                    updateStatus("Camera ready without ImageAnalysis")
                }
            } catch (exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
                try {
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        this,
                        cameraSelector,
                        preview,
                        imageCaptureUseCase,
                        videoCaptureUseCase,
                    )
                    imageAnalysis = null
                    updateUseCases(includeAnalysis = false)
                    updateStatus("Camera ready without ImageAnalysis")
                } catch (fallbackExc: Exception) {
                    Log.e(TAG, "Fallback binding failed", fallbackExc)
                    imageCapture = null
                    videoCapture = null
                    imageAnalysis = null
                    updateStatus("Camera binding failed: ${fallbackExc.message}")
                }
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun takePhoto() {
        val imageCapture = imageCapture ?: run {
            updateStatus("ImageCapture is not ready")
            return
        }

        val name = SimpleDateFormat(FILENAME_FORMAT, Locale.US)
            .format(System.currentTimeMillis())
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            if (Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
                put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/CameraX-Image")
            }
        }

        val outputOptions = ImageCapture.OutputFileOptions.Builder(
            contentResolver,
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            contentValues,
        ).build()

        updateStatus("Taking photo...")
        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onError(exc: ImageCaptureException) {
                    Log.e(TAG, "Photo capture failed: ${exc.message}", exc)
                    updateStatus("Photo capture failed: ${exc.message}")
                }

                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    val savedUri = output.savedUri
                    val msg = "Photo saved: $savedUri"
                    Log.d(TAG, msg)
                    updateStatus(msg)
                    Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                }
            },
        )
    }

    @SuppressLint("MissingPermission")
    private fun captureVideo() {
        val videoCapture = videoCapture ?: run {
            updateStatus("VideoCapture is not ready")
            return
        }

        val currentRecording = recording
        if (currentRecording != null) {
            updateStatus("Stopping recording...")
            currentRecording.stop()
            recording = null
            return
        }

        val name = SimpleDateFormat(FILENAME_FORMAT, Locale.US)
            .format(System.currentTimeMillis())
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")
            if (Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
                put(MediaStore.MediaColumns.RELATIVE_PATH, "Movies/CameraX-Video")
            }
        }

        val mediaStoreOutputOptions = MediaStoreOutputOptions.Builder(
            contentResolver,
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
        )
            .setContentValues(contentValues)
            .build()

        var pendingRecording = videoCapture.output.prepareRecording(this, mediaStoreOutputOptions)
        if (hasPermission(Manifest.permission.RECORD_AUDIO)) {
            pendingRecording = pendingRecording.withAudioEnabled()
        }

        updateStatus("Starting recording...")
        recording = pendingRecording.start(ContextCompat.getMainExecutor(this)) { recordEvent ->
            when (recordEvent) {
                is VideoRecordEvent.Start -> {
                    viewBinding.videoCaptureButton.text = getString(R.string.stop_capture)
                    updateStatus("Recording...")
                }

                is VideoRecordEvent.Finalize -> {
                    if (!recordEvent.hasError()) {
                        val msg = "Video saved: ${recordEvent.outputResults.outputUri}"
                        Log.d(TAG, msg)
                        Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                        updateStatus(msg)
                    } else {
                        recording?.close()
                        recording = null
                        Log.e(
                            TAG,
                            "Video capture failed: ${recordEvent.error}",
                            recordEvent.cause,
                        )
                        updateStatus("Video capture failed: ${recordEvent.error}")
                    }
                    viewBinding.videoCaptureButton.text = getString(R.string.start_capture)
                    recording = null
                }
            }
        }
    }

    private fun switchCamera() {
        isBackCamera = !isBackCamera
        cameraSelector = if (isBackCamera) {
            CameraSelector.DEFAULT_BACK_CAMERA
        } else {
            CameraSelector.DEFAULT_FRONT_CAMERA
        }
        updateStatus(if (isBackCamera) "Switching to back camera" else "Switching to front camera")
        startCamera()
    }

    private fun toggleAnalysis() {
        isAnalysisEnabled = !isAnalysisEnabled
        viewBinding.analysisToggleButton.text = getString(
            if (isAnalysisEnabled) R.string.analysis_on else R.string.analysis_off,
        )
        viewBinding.analysisText.text = if (isAnalysisEnabled) {
            "Analysis: running"
        } else {
            "Analysis: paused"
        }
        startCamera()
    }

    private fun updateStatus(message: String) {
        viewBinding.statusText.text = "Status: $message"
    }

    private fun updateUseCases(includeAnalysis: Boolean) {
        viewBinding.analysisText.text = if (includeAnalysis) {
            "Analysis: running"
        } else {
            "Analysis: paused or unavailable"
        }
        viewBinding.useCaseText.text = if (includeAnalysis) {
            "Use cases: Preview / ImageCapture / VideoCapture / ImageAnalysis"
        } else {
            "Use cases: Preview / ImageCapture / VideoCapture"
        }
    }

    private fun requiredPermissions(): Array<String> {
        val permissions = mutableListOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
        )
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            permissions += Manifest.permission.WRITE_EXTERNAL_STORAGE
        }
        return permissions.toTypedArray()
    }

    private fun allPermissionsGranted(): Boolean =
        requiredPermissions().all { hasPermission(it) }

    private fun hasPermission(permission: String): Boolean =
        ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED

    override fun onDestroy() {
        super.onDestroy()
        recording?.close()
        cameraExecutor.shutdown()
    }

    private class LuminosityAnalyzer(
        private val listener: (Double) -> Unit,
    ) : ImageAnalysis.Analyzer {

        override fun analyze(image: ImageProxy) {
            try {
                val buffer = image.planes[0].buffer
                val data = buffer.toByteArray()
                val pixels = data.map { it.toInt() and 0xFF }
                val luma = pixels.average()

                listener(luma)
            } finally {
                image.close()
            }
        }

        private fun ByteBuffer.toByteArray(): ByteArray {
            rewind()
            val data = ByteArray(remaining())
            get(data)
            return data
        }
    }

    companion object {
        private const val TAG = "CameraXApp"
        private const val FILENAME_FORMAT = "yyyy-MM-dd-HH-mm-ss-SSS"
    }
}
