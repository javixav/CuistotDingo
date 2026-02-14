package org.kivy.library;
import android.content.Context;
import android.media.MediaScannerConnection;
import android.net.Uri;
import java.io.File;

public class MediaStoreNotifier {

    public void notifyMediaStore(Context context, File file) {
        MediaScannerConnection.scanFile(context,
                new String[]{file.getAbsolutePath()},
                null, // Mime type can be null, system will infer
                new MediaScannerConnection.OnScanCompletedListener() {
                    @Override
                    public void onScanCompleted(String path, Uri uri) {
                        // Optional: Handle the completion of the scan
                        // The 'uri' parameter will contain the content URI of the newly added file
                        // You can log this or perform other actions if needed
                    }
                });
    }
    public static void notifyMediaStore_2(Context context, File file) {
        MediaScannerConnection.scanFile(context,
                new String[]{file.getAbsolutePath()},
                null, // Mime type can be null, system will infer
                new MediaScannerConnection.OnScanCompletedListener() {
                    @Override
                    public void onScanCompleted(String path, Uri uri) {
                        // Optional: Handle the completion of the scan
                        // The 'uri' parameter will contain the content URI of the newly added file
                        // You can log this or perform other actions if needed
                    }
                });
    }
}